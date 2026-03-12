import asyncio
import sys
import os
import subprocess

async def standardize_and_check(input_path: str, output_path: str):
    """
    1. Standardizes audio to 16kHz Mono WAV (PCM) as fast as possible.
    2. Checks if projected Base64 size > 100MB.
    """
    print(f"--- Fast Standardization: {input_path} ---")
    
    # Fast PCM conversion (no heavy encoding)
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-ar', '16000', '-ac', '1',
        '-c:a', 'pcm_s16le',
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    
    if process.returncode != 0:
        print(f"FFmpeg failed with return code {process.returncode}")
        return False

    # Calculate projected Base64 size
    file_size = os.path.getsize(output_path)
    projected_base64_mb = (file_size * 1.33) / (1024 * 1024)
    
    print(f"Standardization Complete.")
    print(f"WAV File: {output_path} ({file_size / (1024*1024):.2f} MB)")
    print(f"Projected Base64 Size: {projected_base64_mb:.2f} MB")
    
    if projected_base64_mb > 100:
        print(">>> TRIGGER: Projected size > 100MB. Map-Reduce Chunking REQUIRED.")
        return True
    else:
        print(">>> STATUS: Projected size <= 100MB. Single-Pass Summary OK.")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/fast_standardize.py <input> <output_wav>")
        sys.exit(1)
    
    asyncio.run(standardize_and_check(sys.argv[1], sys.argv[2]))
