import pytest
from unittest.mock import AsyncMock
from app.global_memory_generator import GlobalMemoryGenerator

@pytest.mark.asyncio
async def test_generate_global_memory():
    """Test generating global memory from an audio file."""
    # Mock GeminiClient
    mock_client = AsyncMock()
    mock_client.upload_file.return_value = ("https://file.uri", "files/test_file")
    mock_client.poll_file_state.return_value = True
    mock_client.generate_content.return_value = {
        "theme": "AI and Speech",
        "speakers": [{"id": "Speaker_A", "characteristics": "Calm voice"}],
        "glossary": ["LLM", "VAD"]
    }
    
    generator = GlobalMemoryGenerator(mock_client)
    memory = await generator.generate(b"fake_audio_content")
    
    assert memory["theme"] == "AI and Speech"
    assert len(memory["speakers"]) == 1
    assert "LLM" in memory["glossary"]
    
    # Verify calls
    mock_client.upload_file.assert_called_once()
    mock_client.poll_file_state.assert_called_once_with("files/test_file")
    mock_client.generate_content.assert_called_once()
