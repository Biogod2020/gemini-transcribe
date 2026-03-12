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

def test_normalize_audio_lufs():
    mock_audio = MagicMock()
    # Mock pydub to numpy conversion properties
    mock_audio.get_array_of_samples.return_value = [0] * 1000
    mock_audio.frame_rate = 16000
    mock_audio.sample_width = 2
    mock_audio.channels = 1
    
    with patch("pyloudnorm.Meter") as mock_meter_class:
        mock_meter = mock_meter_class.return_value
        mock_meter.measure.return_value = -25.0
        
        with patch("app.utils.AudioSegment") as mock_as_class:
            from app.utils import normalize_audio_lufs
            result = normalize_audio_lufs(mock_audio, target_lufs=-16.0)
            
            # Should calculate gain: -16.0 - (-25.0) = +9.0 dB
            mock_audio.apply_gain.assert_called_once_with(9.0)

