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
        mock_meter.integrated_loudness.return_value = -25.0
        
        with patch("app.utils.AudioSegment") as mock_as_class:
            from app.utils import normalize_audio_lufs
            result = normalize_audio_lufs(mock_audio, target_lufs=-16.0)
            
            # Should calculate gain: -16.0 - (-25.0) = +9.0 dB
            mock_audio.apply_gain.assert_called_once_with(9.0)

def test_standardize_audio():
    mock_audio = MagicMock()
    
    with patch("app.utils.AudioSegment") as mock_as_class:
        from app.utils import standardize_audio
        result = standardize_audio(mock_audio)
        
        # Should set frame rate to 16000 and channels to 1
        mock_audio.set_frame_rate.assert_called_once_with(16000)
        # set_channels might be chained or separate
        mock_audio.set_frame_rate.return_value.set_channels.assert_called_once_with(1)
        mock_audio.set_frame_rate.return_value.set_channels.return_value.set_sample_width.assert_called_once_with(2)

def test_remove_dc_offset():
    # We can't easily mock the internal array operations of remove_dc_offset
    # without a real AudioSegment or complex mocks.
    # Let's use a real small AudioSegment for this one if possible,
    # or mock the numpy mean/subtraction.
    from pydub import AudioSegment
    import numpy as np
    
    # Create a 10ms silent mono 16kHz segment
    audio = AudioSegment.silent(duration=10, frame_rate=16000)
    
    from app.utils import remove_dc_offset
    result = remove_dc_offset(audio)
    assert isinstance(result, AudioSegment)

def test_add_silence_padding():
    from pydub import AudioSegment
    audio = AudioSegment.silent(duration=100, frame_rate=16000)
    
    from app.utils import add_silence_padding
    # Add 100ms padding to each end
    result = add_silence_padding(audio, padding_ms=100)
    
    assert len(result) == 300 # 100 + 100 + 100

def test_preprocess_audio_global_mode():
    with patch("subprocess.run") as mock_run:
        from app.utils import preprocess_audio
        result = preprocess_audio("test.wav", mode="global")
        
        # Check command has libopus and 32k
        args, kwargs = mock_run.call_args
        command = args[0]
        assert "libopus" in command
        assert "32k" in command
        assert result.endswith(".opus")

def test_preprocess_audio_chunk_mode():
    with patch("subprocess.run") as mock_run:
        from app.utils import preprocess_audio
        result = preprocess_audio("test.wav", mode="chunk")
        
        # Check command has pcm_s16le for high clarity
        args, kwargs = mock_run.call_args
        command = args[0]
        assert "pcm_s16le" in command
        assert result.endswith(".wav")




