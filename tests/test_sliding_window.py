import pytest
from app.transcriber import build_transcription_prompt

def test_sliding_window_logic():
    global_memory = {
        "theme": "Test Theme",
        "glossary": ["Term1"],
        "speakers": [{"id": "Speaker1", "characteristics": "Test"}]
    }
    
    processed_chunks = [
        {"chunk_index": 1, "transcript": "Transcript 1"},
        {"chunk_index": 2, "transcript": "Transcript 2"},
        {"chunk_index": 3, "transcript": "Transcript 3"}
    ]
    
    # Test window size 1
    prompt_w1 = build_transcription_prompt(global_memory, processed_chunks, context_window_size=1)
    assert "第 1 段" not in prompt_w1
    assert "第 2 段" not in prompt_w1
    assert "第 3 段" in prompt_w1
    
    # Test window size 2
    prompt_w2 = build_transcription_prompt(global_memory, processed_chunks, context_window_size=2)
    assert "第 1 段" not in prompt_w2
    assert "第 2 段" in prompt_w2
    assert "第 3 段" in prompt_w2
    
    # Test window size 0
    prompt_w0 = build_transcription_prompt(global_memory, processed_chunks, context_window_size=0)
    assert "历史对齐上下文" not in prompt_w0
    assert "尚无历史转录参考" in prompt_w0

if __name__ == "__main__":
    test_sliding_window_logic()
    print("Sliding window test passed!")
