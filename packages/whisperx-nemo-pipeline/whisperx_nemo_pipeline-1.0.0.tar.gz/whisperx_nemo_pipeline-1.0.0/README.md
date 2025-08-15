# WhisperX-NeMo Pipeline

A production-ready transcription and diarization pipeline with parallel processing.

## Features

- **Parallel Processing**: Runs Whisper transcription and NeMo diarization simultaneously
- **Multiple Backends**: Supports both faster-whisper and WhisperX
- **Speaker Diarization**: Uses NeMo MSDD models for accurate speaker identification
- **Audio Source Separation**: Optional vocal extraction using Demucs
- **Punctuation Restoration**: Automatic punctuation using deep learning models
- **Memory Efficient**: Proper GPU memory management and cleanup

## Installation

```bash
pip install whisperx-nemo-pipeline
```

**With constraints (recommended for production):**
```bash
pip install whisperx-nemo-pipeline -c constraints.txt
```

## Quick Start

```python
from whisperx_nemo_pipeline import create_transcription_pipeline

# Create pipeline
pipeline = create_transcription_pipeline(
    audio_path="path/to/your/audio.wav",
    model_name="large-v2",
    device="cuda",  # or "cpu"
    stemming=True,  # Enable source separation
    backend="faster_whisper"  # or "whisperx"
)

# Process audio
transcript_path, srt_path, timing_info = pipeline.process()

print(f"Transcript saved to: {transcript_path}")
print(f"Subtitles saved to: {srt_path}")
print(f"Processing took: {timing_info['total_time']:.2f}s")
```

## Advanced Usage

```python
from whisperx_nemo_pipeline import TranscriptionPipeline, TranscriptionConfig

# Custom configuration
config = TranscriptionConfig(
    audio_path="path/to/audio.wav",
    model_name="large-v2",
    device="cuda",
    batch_size=8,
    language="en",  # or None for auto-detection
    stemming=True,
    suppress_numerals=False,
    backend="faster_whisper"
)

# Create pipeline with custom config
pipeline = TranscriptionPipeline(config)

# Process
transcript_path, srt_path, timing_info = pipeline.process()
```

## Configuration Options

- `audio_path`: Path to input audio file
- `model_name`: Whisper model size ("tiny", "base", "small", "medium", "large-v2")
- `device`: Computing device ("cuda" or "cpu")
- `batch_size`: Batch size for inference (default: 4)
- `language`: Language code or None for auto-detection
- `stemming`: Enable audio source separation (default: True)
- `suppress_numerals`: Suppress numerical tokens (default: False)
- `backend`: "faster_whisper" or "whisperx"

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- See `requirements.txt` for full dependency list

## License

MIT License