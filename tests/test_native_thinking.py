import pytest
from unittest.mock import AsyncMock
import json
import respx
from app.gemini_client import GeminiClient
from app.config import config

@pytest.mark.asyncio
async def test_generate_content_with_native_thinking():
    """Test that thoughts are correctly extracted and separated from the final answer."""
    client = GeminiClient(api_key="fake_key", model="gemini-3-flash-preview")
    
    # Mock response with thoughts and text parts
    mock_response_body = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "I am thinking about how to transcribe this...", "thought": True},
                        {"text": '[{"speaker_id": "S1", "text": "Hello world"}]'}
                    ]
                }
            }
        ]
    }
    
    url = f"{config.BASE_URL}/models/gemini-3-flash-preview:generateContent?key=fake_key"
    
    with respx.mock:
        respx.post(url).respond(200, json=mock_response_body)
        
        result = await client.generate_content(
            prompt="Transcribe this",
            mime_type="audio/mpeg",
            file_uri="https://file.uri"
        )
        
        assert isinstance(result, dict)
        assert "data" in result
        assert "thought" in result
        assert result["thought"] == "I am thinking about how to transcribe this..."
        assert result["data"][0]["speaker_id"] == "S1"
        assert result["data"][0]["text"] == "Hello world"

@pytest.mark.asyncio
async def test_generate_content_includes_thinking_config():
    """Test that the request payload includes thinking_config."""
    client = GeminiClient(api_key="fake_key", model="gemini-3-flash-preview")
    
    url = f"{config.BASE_URL}/models/gemini-3-flash-preview:generateContent?key=fake_key"
    
    with respx.mock:
        def check_request(request):
            payload = json.loads(request.content)
            gen_config = payload.get("generationConfig", {})
            thinking_config = gen_config.get("thinking_config", {})
            assert thinking_config.get("thinking_level") == "MEDIUM"
            assert thinking_config.get("include_thoughts") is True
            return respx.MockResponse(200, json={"candidates": [{"content": {"parts": [{"text": "[]"}]}}]})

        respx.post(url).mock(side_effect=check_request)
        
        await client.generate_content(
            prompt="Transcribe",
            mime_type="audio/mpeg",
            file_uri="https://file.uri"
        )
