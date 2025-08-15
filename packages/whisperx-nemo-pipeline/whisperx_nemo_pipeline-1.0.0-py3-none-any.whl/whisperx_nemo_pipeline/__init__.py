"""
WhisperX-NeMo Pipeline: Production-ready transcription and diarization

A production-ready transcription and diarization pipeline with parallel processing.
Combines WhisperX/Faster-Whisper for transcription and NeMo for speaker diarization.
"""

from .transcription_pipeline import (
    TranscriptionPipeline,
    TranscriptionConfig,
    TranscriptionResult,
    DiarizationResult,
    create_transcription_pipeline,
)

__version__ = "1.0.0"
__author__ = "Paul Borie"
__email__ = "paul.borie1@gmail.com"

__all__ = [
    "TranscriptionPipeline",
    "TranscriptionConfig", 
    "TranscriptionResult",
    "DiarizationResult",
    "create_transcription_pipeline",
]