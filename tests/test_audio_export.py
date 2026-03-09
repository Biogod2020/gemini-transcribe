import os
import pytest
import numpy as np
from pydub import AudioSegment
from app.audio_exporter import AudioExporter

def test_export_chunks(tmp_path):
    """Test that chunks are correctly exported as separate files."""
    exporter = AudioExporter()
    
    # Create 2 fake chunks (1 second each at 16kHz)
    chunk1 = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
    chunk2 = np.random.uniform(-0.1, 0.1, 16000).astype(np.float32)
    chunks = [chunk1, chunk2]
    
    output_dir = tmp_path / "chunks"
    output_dir.mkdir()
    
    exported_files = exporter.export_chunks(chunks, str(output_dir), prefix="test_chunk")
    
    assert len(exported_files) == 2
    for file_path in exported_files:
        assert os.path.exists(file_path)
        assert file_path.endswith(".mp3")

def test_load_audio(tmp_path):
    """Test loading an audio file into a numpy array."""
    exporter = AudioExporter()
    
    # Create a dummy silent MP3
    silent_audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    audio_path = tmp_path / "silent.mp3"
    silent_audio.export(str(audio_path), format="mp3")
    
    audio_data, sr = exporter.load_audio(str(audio_path))
    
    assert sr == 16000
    assert len(audio_data) == 16000
    assert isinstance(audio_data, np.ndarray)
