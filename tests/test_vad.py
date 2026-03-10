import pytest
import numpy as np
from unittest.mock import MagicMock
from app.vad_processor import VADProcessor

def test_vad_initialization():
    """Test that the VAD processor initializes correctly."""
    processor = VADProcessor()
    assert processor.model is not None

def test_silence_detection(mocker):
    """Test that silence is correctly handled."""
    processor = VADProcessor()
    # Mock the VAD utility to return no segments
    processor.get_speech_timestamps = MagicMock(return_value=[])
    
    silence = np.zeros(16000, dtype=np.float32)
    segments = processor.detect_speech_segments(silence)
    assert len(segments) == 0

def test_speech_detection(mocker):
    """Test that speech is detected."""
    processor = VADProcessor()
    # Mock the VAD utility to return a fake segment
    processor.get_speech_timestamps = MagicMock(return_value=[{'start': 0, 'end': 16000}])
    
    audio = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
    segments = processor.detect_speech_segments(audio)
    assert len(segments) == 1
    assert segments[0]['start'] == 0

def test_chunking_logic(mocker):
    """Test the core chunking/splitting logic with mocked VAD output."""
    processor = VADProcessor(min_silence_duration_ms=100)
    
    # Mock 2 speech segments with a gap (silence) in between
    # Segments: [0-2s], [3-5s]
    # Silence at [2s-3s] (samples 32000-48000)
    processor.get_speech_timestamps = MagicMock(return_value=[
        {'start': 0, 'end': 32000},
        {'start': 48000, 'end': 80000}
    ])
    
    audio = np.random.uniform(-0.1, 0.1, 80000).astype(np.float32)
    
    # Target chunk duration 1 sec, so it should split at the 2.5s mark (40000 samples)
    chunks = processor.get_chunks(audio, sampling_rate=16000, target_chunk_duration_sec=1)
    
    assert len(chunks) == 2
    assert chunks[0].shape[0] == 40000
    assert chunks[1].shape[0] == 40000

def test_chunking_logic_with_bounds(mocker):
    """Test chunking logic adheres to min (7m) and max (10m) bounds."""
    processor = VADProcessor()
    
    sr = 16000
    # Simulate a 25-minute audio (1500 seconds)
    total_duration_sec = 1500
    audio = np.zeros(total_duration_sec * sr, dtype=np.float32)
    
    # Mock speech segments every 1 minute (60s) with brief silences in between
    segments = []
    for i in range(25):
        start = i * 60 * sr
        end = (i * 60 + 58) * sr # 2 seconds of silence
        segments.append({'start': start, 'end': end})
        
    processor.get_speech_timestamps = MagicMock(return_value=segments)
    
    # Should chunk between 7 mins (420s) and 10 mins (600s)
    # With silences every minute, it should ideally split around the 8, 9, or 10 min mark.
    chunks = processor.get_chunks(audio, sampling_rate=sr)
    
    assert len(chunks) > 0
    # The first few chunks must be between 7 and 10 mins (420s to 600s)
    # The last chunk might be shorter, so we don't test the min bound on the very last one.
    for i, chunk in enumerate(chunks[:-1]):
        duration_sec = len(chunk) / sr
        assert 420 <= duration_sec <= 600, f"Chunk {i} duration {duration_sec}s is out of bounds (7-10 mins)"
    
    # Total duration should match
    total_chunked_samples = sum(len(c) for c in chunks)
    assert total_chunked_samples == len(audio)
