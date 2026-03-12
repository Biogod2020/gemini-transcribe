import json
import re
from typing import Any, Optional, Dict
from pydub import AudioSegment
import numpy as np
import pyloudnorm as pyln

def load_audio(file_path: str) -> AudioSegment:
    """
    Loads an audio file into a pydub AudioSegment.
    Supports multiple formats (MP3, M4A, WAV, etc.) via pydub's from_file.
    """
    try:
        return AudioSegment.from_file(file_path)
    except Exception as e:
        # Re-raise or handle as needed for benchmarking robustness
        raise e

def normalize_audio_lufs(audio: AudioSegment, target_lufs: float = -16.0) -> AudioSegment:
    """
    Normalizes the loudness of an AudioSegment to the target LUFS using EBU R128.
    """
    # Convert pydub AudioSegment to numpy array
    # pydub samples are usually int16, we need float32 in range [-1, 1] for pyloudnorm
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    
    # Reshape for multi-channel if necessary (though we usually target mono)
    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels))
    
    # Normalize to [-1, 1] range based on sample width (2 bytes = 16-bit)
    max_val = float(2**(8 * audio.sample_width - 1))
    samples = samples / max_val
    
    # Measure current loudness
    meter = pyln.Meter(audio.frame_rate)
    loudness = meter.integrated_loudness(samples)
    
    # Calculate gain to apply
    gain_db = target_lufs - loudness
    
    return audio.apply_gain(gain_db)

def standardize_audio(audio: AudioSegment) -> AudioSegment:
    """
    Converts AudioSegment to 16kHz, Mono, 16-bit.
    """
    return audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

def remove_dc_offset(audio: AudioSegment) -> AudioSegment:
    """
    Removes DC offset by centering the waveform.
    """
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    mean = np.mean(samples)
    centered_samples = samples - mean
    
    # Convert back to original sample width (usually int16)
    if audio.sample_width == 2:
        centered_samples = centered_samples.astype(np.int16)
    
    return audio._spawn(centered_samples.tobytes())

def add_silence_padding(audio: AudioSegment, padding_ms: int = 100) -> AudioSegment:
    """
    Adds silence padding to the beginning and end of an AudioSegment.
    """
    silence = AudioSegment.silent(duration=padding_ms, frame_rate=audio.frame_rate)
    return silence + audio + silence

def preprocess_audio(file_path: str, target_lufs: float = -16.0, mode: str = "chunk") -> str:
    """
    Full preprocessing pipeline using FFmpeg: Normalize -> Resample -> Transcode.
    
    Modes:
    - "global": High compression (Opus 32kbps) for 100MB limit safety.
    - "chunk": High clarity (WAV PCM) for accuracy.
    
    Returns the path to the preprocessed file.
    """
    if mode == "global":
        output_path = file_path.rsplit('.', 1)[0] + "_global.opus"
        # 16kHz, Mono, 32k bitrate Opus
        codec_args = ["-c:a", "libopus", "-b:a", "32k"]
    else:
        output_path = file_path.rsplit('.', 1)[0] + "_chunk.wav"
        # 16kHz, Mono, PCM 16-bit WAV
        codec_args = ["-c:a", "pcm_s16le"]

    command = [
        "ffmpeg", "-y", "-i", file_path,
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
        "-ar", "16000", "-ac", "1"
    ] + codec_args + [output_path]
    
    import subprocess
    try:
        subprocess.run(command, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg preprocessing failed: {e.stderr.decode()}")
        raise e

def parse_json_response(text: str) -> Any:
    """
    Robustly parses JSON from a model response string.
    Handles cases where the model might wrap JSON in markdown blocks or 
    include leading/trailing explanatory text.
    """
    text = text.strip()
    if not text:
        return None

    # 1. Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Try to find JSON block via regex (Markdown blocks)
    # Search for ```json ... ``` or ``` ... ```
    json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Last ditch attempt: find the outermost brackets
    # This handles text like "Sure, here is your JSON: { ... }"
    start_bracket = text.find('[')
    start_brace = text.find('{')
    
    # Determine which bracket comes first
    if start_bracket != -1 and (start_brace == -1 or start_bracket < start_brace):
        start = start_bracket
        end = text.rfind(']')
    elif start_brace != -1:
        start = start_brace
        end = text.rfind('}')
    else:
        start = -1
        end = -1

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass

    # If all failed, return raw text as fallback (or raise error if strict)
    return text

def extract_content_and_thoughts(response_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Follows official pattern to separate thought parts and text parts from a Gemini response.
    Returns: {"data": parsed_json, "thought": full_thoughts_string}
    """
    candidates = response_payload.get("candidates", [])
    if not candidates:
        return {"data": None, "thought": ""}
        
    parts = candidates[0].get("content", {}).get("parts", [])
    thoughts = []
    text_parts = []
    
    for part in parts:
        part_text = part.get("text", "")
        # Official API uses the 'thought' boolean flag
        if part.get("thought"):
            thoughts.append(part_text)
        else:
            text_parts.append(part_text)
    
    full_thoughts = "\n".join(thoughts).strip()
    combined_text = "".join(text_parts).strip()
    
    parsed_data = parse_json_response(combined_text)
    
    return {"data": parsed_data, "thought": full_thoughts}

def normalize_text(text: Any) -> str:
    """
    Normalizes text for ASR evaluation (WER).
    - Converts input to string if it's not
    - Lowercases
    - Removes punctuation
    - Collapses multiple spaces
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Collapse multiple spaces and strip
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

