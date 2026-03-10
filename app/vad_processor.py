import torch
import numpy as np
from typing import List, Dict

class VADProcessor:
    def __init__(self, min_silence_duration_ms: int = 700, threshold: float = 0.5):
        """
        Initialize the Silero VAD processor.
        
        Args:
            min_silence_duration_ms: Minimum duration of silence to trigger a split.
            threshold: Probability threshold for speech detection.
        """
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        (self.get_speech_timestamps, _, _, _, _) = self.utils
        self.min_silence_duration_ms = min_silence_duration_ms
        self.threshold = threshold

    def detect_speech_segments(self, audio_data: np.ndarray, sampling_rate: int = 16000) -> List[Dict[str, int]]:
        """
        Identify segments of speech in the audio data.
        
        Args:
            audio_data: Numpy array of audio samples (float32).
            sampling_rate: Audio sampling rate (default 16000).
        """
        audio_tensor = torch.from_numpy(audio_data)
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor,
            self.model,
            sampling_rate=sampling_rate,
            threshold=self.threshold,
            min_silence_duration_ms=self.min_silence_duration_ms
        )
        return speech_timestamps

    def get_chunks(self, audio_data: np.ndarray, sampling_rate: int = 16000, target_chunk_duration_sec: int = 420, max_chunk_duration_sec: int = 600) -> List[np.ndarray]:
        """
        Split a long audio buffer into chunks at silence points, enforcing duration bounds.
        
        Args:
            audio_data: Full audio buffer.
            sampling_rate: Audio sampling rate.
            target_chunk_duration_sec: Desired min length of each chunk in seconds (default 7 mins).
            max_chunk_duration_sec: Hard maximum length of each chunk in seconds (default 10 mins).
        """
        speech_segments = self.detect_speech_segments(audio_data, sampling_rate)
        
        if not speech_segments:
            return []
            
        chunks = []
        current_chunk_start = 0
        min_samples = target_chunk_duration_sec * sampling_rate
        max_samples = max_chunk_duration_sec * sampling_rate
        
        last_valid_split = None
        
        for i in range(len(speech_segments) - 1):
            current_segment_end = speech_segments[i]['end']
            next_segment_start = speech_segments[i+1]['start']
            
            # Potential split point is in the middle of the silence
            split_point = (current_segment_end + next_segment_start) // 2
            current_duration = split_point - current_chunk_start
            
            if current_duration >= min_samples:
                if current_duration <= max_samples:
                    # Ideal split point found within bounds
                    chunks.append(audio_data[current_chunk_start:split_point])
                    current_chunk_start = split_point
                    last_valid_split = None
                else:
                    # Exceeded max duration, need to split at the last valid point if we have one,
                    # or just split here if it's the first opportunity (though it violates max bound, it's better than infinite)
                    if last_valid_split is not None:
                        chunks.append(audio_data[current_chunk_start:last_valid_split])
                        current_chunk_start = last_valid_split
                        # Re-evaluate the current split point relative to the new start
                        if (split_point - current_chunk_start) >= min_samples:
                             last_valid_split = split_point
                        else:
                             last_valid_split = None
                    else:
                        # Fallback: force split here to avoid memory issues, even if slightly over max
                        chunks.append(audio_data[current_chunk_start:split_point])
                        current_chunk_start = split_point
            else:
                # Keep tracking potential split points in case we need to fallback
                last_valid_split = split_point
                
        # Append the final remaining part
        if current_chunk_start < len(audio_data):
            # If the last chunk is too long, we could force a split, but VAD relies on silence.
            # For now, append the rest.
            chunks.append(audio_data[current_chunk_start:])
        
        return chunks
