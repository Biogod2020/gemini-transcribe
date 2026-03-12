import asyncio
import os
import sys
from scripts.fast_preprocess import fast_preprocess
from unittest.mock import patch

async def mock_stream_download(url, chunk_size=1024):
    with open("dummy_source.wav", "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

async def test_fast_preprocess_integration():
    low = "test_low.opus"
    high = "test_high.opus"
    
    # Cleanup
    if os.path.exists(low): os.remove(low)
    if os.path.exists(high): os.remove(high)
    
    with patch("scripts.fast_preprocess.stream_download", side_effect=mock_stream_download):
        await fast_preprocess("http://dummy.url", low, high)
    
    assert os.path.exists(low)
    assert os.path.exists(high)
    assert os.path.getsize(low) > 0
    assert os.path.getsize(high) > 0
    
    # Optional: check if low is smaller than high
    print(f"Low size: {os.path.getsize(low)}, High size: {os.path.getsize(high)}")

if __name__ == "__main__":
    asyncio.run(test_fast_preprocess_integration())
