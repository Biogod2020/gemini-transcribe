import json
from app.utils import parse_json_response, extract_content_and_thoughts

def test_parse_json_response_direct():
    data = {"key": "value"}
    assert parse_json_response(json.dumps(data)) == data

def test_parse_json_response_markdown():
    data = [{"speaker_id": "1", "text": "hello"}]
    markdown = f"Here is the result:\n```json\n{json.dumps(data)}\n```"
    assert parse_json_response(markdown) == data

def test_parse_json_response_text_wrap():
    data = {"theme": "test"}
    text = f"The analysis is: {json.dumps(data)}. Hope it helps!"
    assert parse_json_response(text) == data

def test_extract_content_and_thoughts():
    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"thought": True, "text": "I should output JSON."},
                        {"text": '{"result": "success"}'}
                    ]
                }
            }
        ]
    }
    result = extract_content_and_thoughts(payload)
    assert result["thought"] == "I should output JSON."
    assert result["data"] == {"result": "success"}
