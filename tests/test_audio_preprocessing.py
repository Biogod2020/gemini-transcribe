import pytest
from unittest.mock import patch, MagicMock
from app.utils import load_audio

def test_load_audio_mp3():
    with patch("pydub.AudioSegment.from_file") as mock_from_file:
        mock_audio = MagicMock()
        mock_from_file.return_value = mock_audio
        
        result = load_audio("test.mp3")
        
        mock_from_file.assert_called_once_with("test.mp3")
        assert result == mock_audio

def test_load_audio_m4a():
    with patch("pydub.AudioSegment.from_file") as mock_from_file:
        mock_audio = MagicMock()
        mock_from_file.return_value = mock_audio
        
        result = load_audio("test.m4a")
        
        mock_from_file.assert_called_once_with("test.m4a")
        assert result == mock_audio

def test_load_audio_wav():
    with patch("pydub.AudioSegment.from_file") as mock_from_file:
        mock_audio = MagicMock()
        mock_from_file.return_value = mock_audio
        
        result = load_audio("test.wav")
        
        mock_from_file.assert_called_once_with("test.wav")
        assert result == mock_audio

def test_load_audio_error():
    with patch("pydub.AudioSegment.from_file") as mock_from_file:
        mock_from_file.side_effect = Exception("Load failed")
        
        with pytest.raises(Exception, match="Load failed"):
            load_audio("invalid.file")
