import os
import numpy as np
from pydub import AudioSegment
from typing import List, Tuple

# Set the path to the local ffmpeg binary
BIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin')
os.environ["PATH"] += os.pathsep + BIN_DIR

class AudioExporter:
    def __init__(self, sampling_rate: int = 16000):
        self.sampling_rate = sampling_rate

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load an audio file and convert it to a float32 numpy array.
        """
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(self.sampling_rate).set_channels(1)
        
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Normalize to float32 between -1 and 1
        if audio.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        elif audio.sample_width == 4:
            samples = samples.astype(np.float32) / 2147483648.0
            
        return samples, self.sampling_rate

    def export_chunks(self, chunks: List[np.ndarray], output_dir: str, prefix: str = "chunk", format: str = "mp3") -> List[str]:
        """
        Export a list of audio chunks (numpy arrays) as separate audio files.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        exported_files = []
        
        for i, chunk in enumerate(chunks):
            # Denormalize back to int16
            chunk_int16 = (chunk * 32767).astype(np.int16)
            
            # Create AudioSegment
            audio_segment = AudioSegment(
                chunk_int16.tobytes(),
                frame_rate=self.sampling_rate,
                sample_width=2,
                channels=1
            )
            
            file_name = f"{prefix}_{i}.{format}"
            file_path = os.path.join(output_dir, file_name)
            
            audio_segment.export(file_path, format=format)
            exported_files.append(file_path)
            
        return exported_files
