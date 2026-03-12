import asyncio
import sys
import os
import json

async def get_audio_info(file_path: str):
    """
    Uses ffprobe to get audio format and size.
    """
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', file_path
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    data = json.loads(stdout)
    
    format_name = data.get('format', {}).get('format_name', '').lower()
    size_bytes = int(data.get('format', {}).get('size', 0))
    
    return format_name, size_bytes

async def adaptive_standardize(input_path: str, output_path: str):
    """
    SOTA Adaptive Preprocessing:
    - Pass-through if small & compressed.
    - Fast MP3 if large or uncompressed.
    """
    print(f"--- Adaptive Standardization: {input_path} ---")
    
    format_name, size_bytes = await get_audio_info(input_path)
    projected_base64_mb = (size_bytes * 1.33) / (1024 * 1024)
    
    # Logic 1: Smart Pass-through
    # If already compressed (mp3/m4a/mov/etc) and fits in 100MB Base64
    is_compressed = any(ext in format_name for ext in ['mp3', 'm4a', 'aac', 'mov'])
    
    if is_compressed and projected_base64_mb < 95:
        print(f">>> Decision: Pass-through (Source is {format_name}, {projected_base64_mb:.2f}MB Base64)")
        cmd = ['ffmpeg', '-y', '-i', input_path, '-c', 'copy', output_path]
    else:
        # Logic 2: Fast MP3 Compression
        # 32kbps Mono 16kHz is extremely fast and small enough for 5h+ audio
        print(f">>> Decision: Fast Transcode (Source size/format exceeds limit or is raw)")
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-ar', '16000', '-ac', '1',
            '-c:a', 'libmp3lame', '-b:a', '32k',
            output_path
        ]
    
    process = await asyncio.create_subprocess_exec(*cmd, stderr=asyncio.subprocess.DEVNULL)
    await process.wait()
    
    final_size = os.path.getsize(output_path)
    final_base64_mb = (final_size * 1.33) / (1024 * 1024)
    
    print(f"Standardization Complete.")
    print(f"Output File: {output_path} ({final_size / (1024*1024):.2f} MB)")
    print(f"Final Base64 Size: {final_base64_mb:.2f} MB")
    
    if final_base64_mb > 100:
        print("!!! WARNING: Still exceeds 100MB. Map-Reduce Required.")
        return "map-reduce"
    else:
        print(">>> SUCCESS: Single-Pass Summary Enabled.")
        return "single-pass"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/fast_standardize.py <input> <output>")
        sys.exit(1)
    
    asyncio.run(adaptive_standardize(sys.argv[1], sys.argv[2]))
