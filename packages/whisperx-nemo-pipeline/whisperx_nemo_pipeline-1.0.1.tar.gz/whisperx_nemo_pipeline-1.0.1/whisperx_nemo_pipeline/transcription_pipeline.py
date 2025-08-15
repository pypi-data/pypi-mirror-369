"""
Production-ready transcription and diarization pipeline with parallel processing.

This module refactors the functionality from diarize_parallel.py and nemo_process.py
into a clean, maintainable class-based architecture with parallel execution.
"""

import logging
import multiprocessing as mp
import os
import re
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

import faster_whisper
#import whisperx
import torch
from pydub import AudioSegment

# Import existing helper functions
import sys
import os

from ctc_forced_aligner import (
    generate_emissions,
    get_alignments,
    get_spans,
    load_alignment_model,
    postprocess_results,
    preprocess_text,
)
from deepmultilingualpunctuation import PunctuationModel
from nemo.collections.asr.models.msdd_models import NeuralDiarizer

from helpers import (
    cleanup,
    create_config,
    find_numeral_symbol_tokens,
    generate_srt_content,
    get_realigned_ws_mapping_with_punctuation,
    get_sentences_speaker_mapping,
    get_speaker_aware_transcript,
    get_words_speaker_mapping,
    langs_to_iso,
    process_language_arg,
    punct_model_langs,
    whisper_langs,
    write_srt,
)


@dataclass
class TranscriptionResult:
    """Results from the transcription process."""
    segments: List[Dict[str, Any]]
    info: Any
    full_transcript: str
    word_timestamps: List[Dict[str, Any]]
    processing_time: float


@dataclass
class DiarizationResult:
    """Results from the diarization process."""
    speaker_timestamps: List[List[int]]
    processing_time: float


@dataclass
class PipelineResult:
    """Complete pipeline results with all requested data."""
    word_timestamps: List[Dict[str, Any]]
    language: str
    srt_content: str
    total_time: float
    backend: str


@dataclass
class TranscriptionConfig:
    """Configuration for the transcription pipeline."""
    audio_path: str
    model_name: str = "large-v2"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 4
    language: Optional[str] = None
    stemming: bool = True
    suppress_numerals: bool = False
    temp_dir: Optional[str] = None
    backend: str = "faster_whisper"  # "faster_whisper" or "whisperx"


class TranscriptionPipeline:
    """
    Production-ready transcription and diarization pipeline.
    
    Handles parallel execution of Whisper transcription and NeMo diarization
    while managing PyTorch GPU memory efficiently.
    """
    
    COMPUTE_TYPES = {"cpu": "int8", "cuda": "float16"}
    
    def __init__(self, config: TranscriptionConfig, loaded_model: Optional[Any] = None):
        self.config = config
        self.temp_dir = config.temp_dir or f"temp_outputs_{os.getpid()}"
        self.vocal_target = None
        self.loaded_model = loaded_model
        
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore", category=UserWarning)
        logging.basicConfig(level=logging.INFO)
        
    def _prepare_audio(self) -> str:
        """Prepare audio file with optional source separation."""
        if not self.config.stemming:
            return self.config.audio_path
            
        logging.info("Starting audio source separation...")
        start_time = time.time()
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        return_code = os.system(
            f'python -m demucs.separate -n htdemucs --two-stems=vocals '
            f'"{self.config.audio_path}" -o "{self.temp_dir}" '
            f'--device "{self.config.device}"'
        )
        
        if return_code != 0:
            logging.warning(
                "Source separation failed, using original audio file. "
                "Use stemming=False to disable it."
            )
            vocal_target = self.config.audio_path
        else:
            vocal_target = os.path.join(
                self.temp_dir,
                "htdemucs",
                os.path.splitext(os.path.basename(self.config.audio_path))[0],
                "vocals.wav",
            )
        
        elapsed = time.time() - start_time
        logging.info(f"Audio preparation completed in {elapsed:.2f}s")
        return vocal_target
        
    def _transcribe_audio(self, vocal_target: str) -> TranscriptionResult:
        """Transcribe audio using either faster_whisper or whisperx backend."""
        start_time = time.time()
        
        if self.config.backend == "whisperx":
            if self.loaded_model is not None:
                return self._transcribe_with_loaded_whisperx(vocal_target, start_time)
            else:
                return self._transcribe_with_whisperx(vocal_target, start_time)
        else:
            return self._transcribe_with_faster_whisper(vocal_target, start_time)
    
    def _transcribe_with_whisperx(self, vocal_target: str, start_time: float) -> TranscriptionResult:
        """Transcribe audio using WhisperX backend."""
        # Prepare ASR options for WhisperX
        asr_options = {
            "suppress_numerals": self.config.suppress_numerals,
        }
        
        # Load WhisperX model
        whisper_model = whisperx.load_model(
            self.config.model_name, 
            device=self.config.device, 
            compute_type=self.COMPUTE_TYPES[self.config.device],
            language=self.config.language,
            asr_options=asr_options
        )
        
        # Load audio
        audio = whisperx.load_audio(vocal_target)
        
        # Transcribe
        result = whisper_model.transcribe(audio, batch_size=self.config.batch_size)
        
        # Convert WhisperX format to match faster_whisper format
        segments_list = result['segments']
        full_transcript = "".join(segment['text'] for segment in segments_list)
        
        # Create mock info object to match faster_whisper format
        class MockInfo:
            def __init__(self, language):
                self.language = language
        
        info = MockInfo(result['language'])
        
        # Forced alignment (same as before)
        alignment_model, alignment_tokenizer = load_alignment_model(
            self.config.device,
            dtype=torch.float16 if self.config.device == "cuda" else torch.float32,
        )
        
        emissions, stride = generate_emissions(
            alignment_model,
            torch.from_numpy(audio)
            .to(alignment_model.dtype)
            .to(alignment_model.device),
            batch_size=self.config.batch_size,
        )
        
        # Clean up alignment model
        del alignment_model
        torch.cuda.empty_cache()
        
        tokens_starred, text_starred = preprocess_text(
            full_transcript,
            romanize=True,
            language=langs_to_iso[info.language],
        )
        
        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )
        
        spans = get_spans(tokens_starred, segments, blank_token)
        word_timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        # Clean up WhisperX model
        del whisper_model
        torch.cuda.empty_cache()
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            segments=segments_list,
            info=info,
            full_transcript=full_transcript,
            word_timestamps=word_timestamps,
            processing_time=processing_time
        )
    
    def _transcribe_with_loaded_whisperx(self, vocal_target: str, start_time: float) -> TranscriptionResult:
        """Transcribe audio using pre-loaded WhisperX model."""
        
        # Use the already loaded WhisperX model
        whisper_model = self.loaded_model
        
        # Load audio
        audio = whisperx.load_audio(vocal_target)
        
        # Transcribe
        result = whisper_model.transcribe(audio, batch_size=self.config.batch_size)
        
        # Convert WhisperX format to match faster_whisper format
        segments_list = result['segments']
        full_transcript = "".join(segment['text'] for segment in segments_list)
        
        # Create mock info object to match faster_whisper format
        class MockInfo:
            def __init__(self, language):
                self.language = language
        
        info = MockInfo(result['language'])
        
        # Forced alignment (same as before)
        alignment_model, alignment_tokenizer = load_alignment_model(
            self.config.device,
            dtype=torch.float16 if self.config.device == "cuda" else torch.float32,
        )
        
        emissions, stride = generate_emissions(
            alignment_model,
            torch.from_numpy(audio)
            .to(alignment_model.dtype)
            .to(alignment_model.device),
            batch_size=self.config.batch_size,
        )
        
        # Clean up alignment model
        del alignment_model
        torch.cuda.empty_cache()
        
        tokens_starred, text_starred = preprocess_text(
            full_transcript,
            romanize=True,
            language=langs_to_iso[info.language],
        )
        
        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )
        
        spans = get_spans(tokens_starred, segments, blank_token)
        word_timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        # Note: We don't delete the loaded model as it may be reused
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            segments=segments_list,
            info=info,
            full_transcript=full_transcript,
            word_timestamps=word_timestamps,
            processing_time=processing_time
        )
    
    def _transcribe_with_faster_whisper(self, vocal_target: str, start_time: float) -> TranscriptionResult:
        """Transcribe audio using faster_whisper backend."""
        # Load Whisper model
        whisper_model = faster_whisper.WhisperModel(
            self.config.model_name,
            device=self.config.device,
            compute_type=self.COMPUTE_TYPES[self.config.device]
        )
        
        whisper_pipeline = faster_whisper.BatchedInferencePipeline(whisper_model)
        audio_waveform = faster_whisper.decode_audio(vocal_target)
        
        language = process_language_arg(self.config.language, self.config.model_name)
        
        suppress_tokens = (
            find_numeral_symbol_tokens(whisper_model.hf_tokenizer)
            if self.config.suppress_numerals
            else [-1]
        )
        
        # Transcribe
        if self.config.batch_size > 0:
            transcript_segments, info = whisper_pipeline.transcribe(
                audio_waveform,
                language,
                suppress_tokens=suppress_tokens,
                batch_size=self.config.batch_size,
            )
        else:
            transcript_segments, info = whisper_model.transcribe(
                audio_waveform,
                language,
                suppress_tokens=suppress_tokens,
                vad_filter=True,
            )
        
        # Convert to list for serialization
        segments_list = list(transcript_segments)
        full_transcript = "".join(segment.text for segment in segments_list)
        
        # Forced alignment
        alignment_model, alignment_tokenizer = load_alignment_model(
            self.config.device,
            dtype=torch.float16 if self.config.device == "cuda" else torch.float32,
        )
        
        emissions, stride = generate_emissions(
            alignment_model,
            torch.from_numpy(audio_waveform)
            .to(alignment_model.dtype)
            .to(alignment_model.device),
            batch_size=self.config.batch_size,
        )
        
        # Clean up alignment model
        del alignment_model
        torch.cuda.empty_cache()
        
        tokens_starred, text_starred = preprocess_text(
            full_transcript,
            romanize=True,
            language=langs_to_iso[info.language],
        )
        
        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            alignment_tokenizer,
        )
        
        spans = get_spans(tokens_starred, segments, blank_token)
        word_timestamps = postprocess_results(text_starred, spans, stride, scores)
        
        # Clean up Whisper model
        del whisper_model, whisper_pipeline
        torch.cuda.empty_cache()
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            segments=segments_list,
            info=info,
            full_transcript=full_transcript,
            word_timestamps=word_timestamps,
            processing_time=processing_time
        )
        
    def _diarize_audio(self, vocal_target: str) -> DiarizationResult:
        """Perform speaker diarization using NeMo in a separate process."""
        start_time = time.time()
        
        # Convert audio to mono for NeMo compatibility
        sound = AudioSegment.from_file(vocal_target).set_channels(1)
        temp_path = os.path.join(os.getcwd(), self.temp_dir)
        os.makedirs(temp_path, exist_ok=True)
        
        mono_file_path = os.path.join(temp_path, "mono_file.wav")
        sound.export(mono_file_path, format="wav")
        
        # Initialize and run NeMo diarization
        msdd_model = NeuralDiarizer(cfg=create_config(temp_path)).to(self.config.device)
        msdd_model.diarize()
        
        # Parse RTTM results
        speaker_ts = []
        rttm_path = os.path.join(temp_path, "pred_rttms", "mono_file.rttm")
        
        with open(rttm_path, "r") as f:
            for line in f:
                line_list = line.split(" ")
                start_ms = int(float(line_list[5]) * 1000)
                end_ms = start_ms + int(float(line_list[8]) * 1000)
                speaker_id = int(line_list[11].split("_")[-1])
                speaker_ts.append([start_ms, end_ms, speaker_id])
        
        # Clean up
        del msdd_model
        torch.cuda.empty_cache()
        
        processing_time = time.time() - start_time
        
        return DiarizationResult(
            speaker_timestamps=speaker_ts,
            processing_time=processing_time
        )
        
    def _apply_punctuation(self, wsm: List[Dict], language: str) -> List[Dict]:
        """Apply punctuation restoration if supported for the language."""
        if language not in punct_model_langs:
            logging.warning(
                f"Punctuation restoration not available for {language}. "
                "Using original punctuation."
            )
            return wsm
            
        punct_model = PunctuationModel(model="kredor/punctuate-all")
        words_list = [x["word"] for x in wsm]
        labeled_words = punct_model.predict(words_list, chunk_size=230)
        
        ending_puncts = ".?!"
        model_puncts = ".,;:!?"
        is_acronym = lambda x: re.fullmatch(r"\b(?:[a-zA-Z]\.){2,}", x)
        
        for word_dict, labeled_tuple in zip(wsm, labeled_words):
            word = word_dict["word"]
            if (
                word
                and labeled_tuple[1] in ending_puncts
                and (word[-1] not in model_puncts or is_acronym(word))
            ):
                word += labeled_tuple[1]
                if word.endswith(".."):
                    word = word.rstrip(".")
                word_dict["word"] = word
                
        return wsm
        
    def process(self) -> PipelineResult:
        """
        Run the complete transcription and diarization pipeline with parallel processing.
        Returns:
            PipelineResult containing word timestamps, language, SRT content, and timing info
        """
        total_start_time = time.time()

        # Prepare audio before forking
        self.vocal_target = self._prepare_audio()

        # On Linux/macOS, use 'fork' for near-instant process startup
        ctx = mp.get_context("fork")

        # Use ProcessPoolExecutor for true parallelism with faster startup
        with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as executor:
            transcription_future = executor.submit(
                _transcribe_worker,
                self.vocal_target,
                self.config,
                self.temp_dir
            )
            diarization_future = executor.submit(
                _diarize_worker,
                self.vocal_target,
                self.config,
                self.temp_dir
            )

            # Wait for both tasks to finish
            transcription_result = transcription_future.result()
            diarization_result = diarization_future.result()

        # Combine results
        logging.info("Combining transcription and diarization results...")

        wsm = get_words_speaker_mapping(
            transcription_result.word_timestamps,
            diarization_result.speaker_timestamps,
            "start"
        )

        # Apply punctuation
        wsm = self._apply_punctuation(wsm, transcription_result.info.language)
        wsm = get_realigned_ws_mapping_with_punctuation(wsm)
        ssm = get_sentences_speaker_mapping(wsm, diarization_result.speaker_timestamps)

        # Generate SRT content in memory
        srt_content = generate_srt_content(ssm)

        # Cleanup temporary files
        cleanup(os.path.join(os.getcwd(), self.temp_dir))

        # Calculate timing
        total_time = time.time() - total_start_time

        return PipelineResult(
            word_timestamps=transcription_result.word_timestamps,
            language=transcription_result.info.language,
            srt_content=srt_content,
            total_time=total_time,
            backend=self.config.backend
        )



def _transcribe_worker(vocal_target: str, config: TranscriptionConfig, temp_dir: str) -> TranscriptionResult:
    """Worker function for transcription - runs in separate process."""
    # Create a new pipeline instance for this process
    worker_config = TranscriptionConfig(
        audio_path=vocal_target,
        model_name=config.model_name,
        device=config.device,
        batch_size=config.batch_size,
        language=config.language,
        suppress_numerals=config.suppress_numerals,
        temp_dir=temp_dir
    )
    
    pipeline = TranscriptionPipeline(worker_config)
    return pipeline._transcribe_audio(vocal_target)


def _diarize_worker(vocal_target: str, config: TranscriptionConfig, temp_dir: str) -> DiarizationResult:
    """Worker function for diarization - runs in separate process."""
    worker_config = TranscriptionConfig(
        audio_path=vocal_target,
        device=config.device,
        temp_dir=temp_dir
    )
    
    pipeline = TranscriptionPipeline(worker_config)
    return pipeline._diarize_audio(vocal_target)


def create_transcription_pipeline(
    audio_path: str,
    model_name: str = "large-v2",
    device: Optional[str] = None,
    batch_size: int = 4,
    language: Optional[str] = None,
    stemming: bool = True,
    suppress_numerals: bool = False,
    backend: str = "faster_whisper"
) -> TranscriptionPipeline:
    """
    Factory function to create a transcription pipeline with sensible defaults.
    
    Args:
        audio_path: Path to the audio file to process
        model_name: Whisper model name (default: large-v2)
        device: Device to use ('cuda' or 'cpu', auto-detected if None)
        batch_size: Batch size for inference (default: 4)
        language: Language code (auto-detected if None)
        stemming: Whether to perform source separation (default: True)
        suppress_numerals: Whether to suppress numerical digits (default: False)
        backend: Transcription backend ('faster_whisper' or 'whisperx', default: faster_whisper)
        
    Returns:
        Configured TranscriptionPipeline instance
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
    config = TranscriptionConfig(
        audio_path=audio_path,
        model_name=model_name,
        device=device,
        batch_size=batch_size,
        language=language,
        stemming=stemming,
        suppress_numerals=suppress_numerals,
        backend=backend
    )
    
    return TranscriptionPipeline(config)


