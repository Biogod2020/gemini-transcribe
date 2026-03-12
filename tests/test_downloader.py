import httpx
import pytest
import respx
from app.downloader import stream_download

@pytest.mark.asyncio
@respx.mock
async def test_stream_download():
    url = "https://example.com/audio.mp3"
    content = b"fake audio content"
    respx.get(url).mock(return_value=httpx.Response(200, content=content))
    
    downloaded_content = b""
    async for chunk in stream_download(url):
        downloaded_content += chunk
    
    assert downloaded_content == content

@pytest.mark.asyncio
@respx.mock
async def test_stream_download_failure():
    url = "https://example.com/audio.mp3"
    respx.get(url).mock(return_value=httpx.Response(404))
    
    with pytest.raises(httpx.HTTPStatusError):
        async for _ in stream_download(url):
            pass
