import asyncio
import sys
from app.downloader import stream_download

async def fast_preprocess(url: str, output_low: str, output_high: str):
    """
    Downloads from URL and pipes to two ffmpeg processes concurrently using asyncio.
    """
    # Global Pass Output: 16kHz, Mono, -16 LUFS, Opus 32kbps
    ffmpeg_low_cmd = [
        'ffmpeg', '-y', '-i', 'pipe:0',
        '-af', 'loudnorm=I=-16.0:LRA=11:TP=-1.5',
        '-ar', '16000', '-ac', '1',
        '-c:a', 'libopus', '-b:a', '32k',
        output_low
    ]
    
    # High-Quality Reference Output: 128kbps Opus (preserving quality for chunking)
    ffmpeg_high_cmd = [
        'ffmpeg', '-y', '-i', 'pipe:0',
        '-c:a', 'libopus', '-b:a', '128k',
        output_high
    ]

    # Start both processes
    proc_low = await asyncio.create_subprocess_exec(
        *ffmpeg_low_cmd,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    
    proc_high = await asyncio.create_subprocess_exec(
        *ffmpeg_high_cmd,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    try:
        async for chunk in stream_download(url):
            # Write to both concurrently and handle backpressure
            if proc_low.stdin and not proc_low.stdin.is_closing():
                proc_low.stdin.write(chunk)
                await proc_low.stdin.drain()
            if proc_high.stdin and not proc_high.stdin.is_closing():
                proc_high.stdin.write(chunk)
                await proc_high.stdin.drain()
            
            # Simple yield to avoid blocking
            await asyncio.sleep(0)
            
    except Exception as e:
        print(f"Error during streaming: {e}", file=sys.stderr)
    finally:
        # Close stdins to signal EOF to ffmpeg
        if proc_low.stdin:
            proc_low.stdin.close()
        if proc_high.stdin:
            proc_high.stdin.close()
        
        # Wait for processes to finish
        await asyncio.gather(
            proc_low.wait(),
            proc_high.wait()
        )
        
        if proc_low.returncode != 0:
            print(f"FFmpeg low-quality process failed with return code {proc_low.returncode}", file=sys.stderr)
        if proc_high.returncode != 0:
            print(f"FFmpeg high-quality process failed with return code {proc_high.returncode}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/fast_preprocess.py <url> <output_low> <output_high>")
        sys.exit(1)
    
    url = sys.argv[1]
    low = sys.argv[2]
    high = sys.argv[3]
    
    asyncio.run(fast_preprocess(url, low, high))
