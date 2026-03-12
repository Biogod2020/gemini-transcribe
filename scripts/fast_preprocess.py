import asyncio
import sys
import os
import subprocess
import json
from app.downloader import stream_download

async def get_audio_bitrate(file_path: str) -> int:
    """
    Uses ffprobe to get the audio bitrate of a local file in bps.
    Returns 128000 (128kbps) as default if detection fails.
    """
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_streams', '-select_streams', 'a', file_path
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        data = json.loads(stdout)
        if 'streams' in data and len(data['streams']) > 0:
            return int(data['streams'][0].get('bit_rate', 128000))
    except Exception:
        pass
    return 128000

async def stream_local_file(file_path: str, chunk_size: int = 1024 * 1024):
    """
    Simulates a stream download from a local file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Local file not found: {file_path}")
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

async def fast_preprocess(source: str, output_original: str, output_low: str, output_high: str, is_url: bool = True):
    """
    Reads from a source (URL or local file) and pipes to two ffmpeg processes and a raw file concurrently.
    """
    # 1. Smart Bitrate Detection (if local)
    source_bitrate = 128000
    if not is_url:
        source_bitrate = await get_audio_bitrate(source)
        print(f"Detected source bitrate: {source_bitrate / 1000:.1f} kbps")

    # Determine target bitrates to avoid bloat
    target_low_kbps = min(32, int(source_bitrate / 1000 * 0.5))
    target_high_kbps = min(128, int(source_bitrate / 1000))
    
    # Ensure a reasonable minimum
    target_low_kbps = max(16, target_low_kbps)
    target_high_kbps = max(32, target_high_kbps)

    print(f"Target bitrates: Low={target_low_kbps}kbps, High={target_high_kbps}kbps")

    # Global Pass Output: 16kHz, Mono, Normalized, Opus
    ffmpeg_low_cmd = [
        'ffmpeg', '-y', '-i', 'pipe:0',
        '-af', 'speechnorm=e=4:r=0.0001:l=1', 
        '-ar', '16000', '-ac', '1',
        '-c:a', 'libopus', '-b:a', f'{target_low_kbps}k',
        output_low
    ]
    
    # High-Quality Reference Output: Opus (Capped at original bitrate)
    ffmpeg_high_cmd = [
        'ffmpeg', '-y', '-i', 'pipe:0',
        '-c:a', 'libopus', '-b:a', f'{target_high_kbps}k',
        output_high
    ]

    # Start both ffmpeg processes
    proc_low = await asyncio.create_subprocess_exec(
        *ffmpeg_low_cmd, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )
    
    proc_high = await asyncio.create_subprocess_exec(
        *ffmpeg_high_cmd, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
    )

    # Choose stream source
    stream = stream_download(source) if is_url else stream_local_file(source)

    # Open the original file for writing
    try:
        with open(output_original, "wb") as f_orig:
            async for chunk in stream:
                f_orig.write(chunk)
                if proc_low.stdin and not proc_low.stdin.is_closing():
                    proc_low.stdin.write(chunk)
                    await proc_low.stdin.drain()
                if proc_high.stdin and not proc_high.stdin.is_closing():
                    proc_high.stdin.write(chunk)
                    await proc_high.stdin.drain()
                await asyncio.sleep(0)
    except Exception as e:
        print(f"Error during streaming: {e}", file=sys.stderr)
    finally:
        if proc_low.stdin: proc_low.stdin.close()
        if proc_high.stdin: proc_high.stdin.close()
        await asyncio.gather(proc_low.wait(), proc_high.wait())
        
        print(f"Preprocessing complete.")
        print(f"Original: {output_original} ({os.path.getsize(output_original)} bytes)")
        if os.path.exists(output_low):
            print(f"Low Quality: {output_low} ({os.path.getsize(output_low)} bytes)")
        if os.path.exists(output_high):
            print(f"High Quality: {output_high} ({os.path.getsize(output_high)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python scripts/fast_preprocess.py <url_or_path> <output_orig> <output_low> <output_high> [--local]")
        sys.exit(1)
    
    source = sys.argv[1]
    orig = sys.argv[2]
    low = sys.argv[3]
    high = sys.argv[4]
    is_url = "--local" not in sys.argv
    
    asyncio.run(fast_preprocess(source, orig, low, high, is_url))
