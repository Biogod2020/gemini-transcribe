from typing import AsyncGenerator
import httpx

async def stream_download(url: str, chunk_size: int = 1024 * 1024) -> AsyncGenerator[bytes, None]:
    """
    Streams a download from a URL in chunks.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                yield chunk
