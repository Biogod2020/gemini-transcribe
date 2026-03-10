import pytest
import httpx
import respx
from app.gemini_client import GeminiClient

@pytest.mark.asyncio
async def test_upload_file():
    """Test the asynchronous file upload to Google File API."""
    client = GeminiClient(api_key="fake_key")
    
    with respx.mock:
        # Mock the metadata upload
        respx.post("https://generativelanguage.googleapis.com/upload/v1beta/files?key=fake_key").respond(
            200, 
            headers={"X-Goog-Upload-URL": "https://upload.url"}
        )
        # Mock the actual file data upload
        respx.put("https://upload.url").respond(
            200, 
            json={"file": {"uri": "https://file.uri", "name": "files/test_file"}}
        )
        
        file_uri, file_name = await client.upload_file("dummy_content", mime_type="audio/mp3", display_name="test_audio")
        
        assert file_uri == "https://file.uri"
        assert file_name == "files/test_file"

@pytest.mark.asyncio
async def test_poll_file_state():
    """Test polling the file state until it is ACTIVE."""
    client = GeminiClient(api_key="fake_key")
    
    with respx.mock:
        # First call returns PROCESSING, second returns ACTIVE
        route = respx.get("https://generativelanguage.googleapis.com/v1beta/files/test_file?key=fake_key")
        route.side_effect = [
            httpx.Response(200, json={"state": "PROCESSING"}),
            httpx.Response(200, json={"state": "ACTIVE"})
        ]
        
        is_active = await client.poll_file_state("files/test_file", interval=0.1, max_retries=2)
        assert is_active is True

@pytest.mark.asyncio
async def test_generate_content():
    """Test content generation with a file URI."""
    client = GeminiClient(api_key="fake_key", model="gemini-3.1-flash-lite-preview")
    
    with respx.mock:
        respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key=fake_key").respond(
            200, 
            json={"candidates": [{"content": {"parts": [{"text": '{"theme": "test"}'}]}}]}
        )
        
        response = await client.generate_content(
            prompt="summarize this", 
            file_uri="https://file.uri", 
            mime_type="audio/mp3"
        )
        
        assert response["theme"] == "test"
