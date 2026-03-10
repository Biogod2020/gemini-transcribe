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

def test_build_prompt_refactored():
    """Test that the refactored prompt contains guidelines but NO manual CoT instructions."""
    global_memory = {"theme": "Full Context Test", "glossary": [], "speakers": []}
    processed_chunks = [{"chunk_index": 0, "transcript": "CHUNK 0"}]
    
    prompt = build_transcription_prompt(global_memory, processed_chunks)
    
    # Should contain guidelines/standards
    assert "转录理解准则" in prompt
    
    # Should NOT contain manual CoT "think step by step" instructions
    assert "一步一步的思考和分析" not in prompt
    assert "Chain-of-Thought" not in prompt
    assert "思考结束后" not in prompt

def test_parse_transcription_response_cot():
    """Test parsing JSON preceded by Chain-of-Thought text."""
    response = "首先，由于音频提到...因此我分析这是讲X。下面是转写结果：\n```json\n[{\"speaker_id\": \"S1\", \"text\": \"Hello\"}]\n```"
    parsed = parse_transcription_response(response)
    assert len(parsed) == 1
    assert parsed[0]["speaker_id"] == "S1"

def test_parse_transcription_response_cot_no_markdown():
    """Test parsing JSON preceded by CoT text without markdown blocks."""
    response = "I think the speaker is S2 because... So here is the array: [{\"speaker_id\": \"S2\", \"text\": \"World\"}]"
    parsed = parse_transcription_response(response)
    assert len(parsed) == 1
    assert parsed[0]["speaker_id"] == "S2"

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
