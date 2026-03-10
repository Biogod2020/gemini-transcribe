import pytest
import json
from app.transcriber import build_transcription_prompt, parse_transcription_response

def test_build_prompt_no_history():
    """Test prompt generation for the first chunk with no history."""
    global_memory = {
        "theme": "Test Theme",
        "glossary": ["Term1", "Term2"],
        "speakers": [{"id": "Speaker_A", "characteristics": "Fast talker"}]
    }
    processed_chunks = []
    
    prompt = build_transcription_prompt(global_memory, processed_chunks)
    
    assert "Test Theme" in prompt
    assert "Term1" in prompt
    assert "Speaker_A" in prompt
    assert "无历史转录" in prompt

def test_build_prompt_sliding_window_n_minus_2():
    """Test that prompt ONLY includes N-1 and N-2 chunks even with long history."""
    global_memory = {"theme": "Sliding Window Test", "glossary": [], "speakers": []}
    processed_chunks = [
        {"chunk_index": 0, "transcript": "CHUNK 0 CONTENT"},
        {"chunk_index": 1, "transcript": "CHUNK 1 CONTENT"},
        {"chunk_index": 2, "transcript": "CHUNK 2 CONTENT"},
        {"chunk_index": 3, "transcript": "CHUNK 3 CONTENT"}
    ]
    
    prompt = build_transcription_prompt(global_memory, processed_chunks)
    
    # Should include 2 and 3
    assert "CHUNK 2 CONTENT" in prompt
    assert "CHUNK 3 CONTENT" in prompt
    
    # Should NOT include 0 and 1 (Sliding window check)
    assert "CHUNK 0 CONTENT" not in prompt
    assert "CHUNK 1 CONTENT" not in prompt

def test_parse_transcription_response_json():
    """Test parsing a clean JSON response."""
    response = '[{"speaker_id": "S1", "text": "Hello"}]'
    parsed = parse_transcription_response(response)
    assert len(parsed) == 1
    assert parsed[0]["speaker_id"] == "S1"

def test_parse_transcription_response_markdown():
    """Test parsing JSON wrapped in Markdown code blocks."""
    response = "Here is the result:\n```json\n[{\"speaker_id\": \"S2\", \"text\": \"World\"}]\n```"
    parsed = parse_transcription_response(response)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "World"

def test_parse_transcription_response_invalid():
    """Test handling of invalid JSON."""
    response = "This is not JSON at all."
    parsed = parse_transcription_response(response)
    assert parsed == []
