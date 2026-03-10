import json
import asyncio
import httpx
import base64
from typing import Tuple, Dict, Any
from app.config import config

class GeminiClient:
    def __init__(self, api_key: str = config.API_KEY, model: str = config.DEFAULT_MODEL, use_inline_data: bool = config.USE_INLINE_DATA, thinking_level: str = config.THINKING_LEVEL):
        self.api_key = api_key
        self.model = model
        self.base_url = config.BASE_URL
        self.upload_url = config.UPLOAD_URL
        self.use_inline_data = use_inline_data
        self.thinking_level = thinking_level

    async def upload_file(self, content: bytes, mime_type: str, display_name: str) -> Tuple[str, str]:
        """
        Upload a file using the resumable upload protocol.
        Returns: (file_uri, file_name)
        """
        if self.use_inline_data:
            return "inline_mode", "inline_mode"
            
        headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(len(content)),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json"
        }
        
        metadata = {"file": {"display_name": display_name}}
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.upload_url}?key={self.api_key}",
                headers=headers,
                json=metadata
            )
            if resp.status_code >= 400:
                print(f"Error starting upload: {resp.status_code} - {resp.text}")
            resp.raise_for_status()
            upload_url = resp.headers["X-Goog-Upload-URL"]
            
            resp = await client.put(
                upload_url,
                headers={
                    "X-Goog-Upload-Command": "upload, finalize",
                    "X-Goog-Upload-Offset": "0",
                    "Content-Length": str(len(content))
                },
                content=content
            )
            resp.raise_for_status()
            
            file_info = resp.json()["file"]
            return file_info["uri"], file_info["name"]

    async def poll_file_state(self, file_name: str, interval: float = 2.0, max_retries: int = 30) -> bool:
        """
        Poll the file state until it's ACTIVE.
        """
        if self.use_inline_data:
            return True
            
        async with httpx.AsyncClient() as client:
            for _ in range(max_retries):
                resp = await client.get(f"{self.base_url}/{file_name}?key={self.api_key}")
                resp.raise_for_status()
                state = resp.json().get("state")
                
                if state == "ACTIVE":
                    return True
                elif state == "FAILED":
                    return False
                    
                await asyncio.sleep(interval)
        return False

    async def generate_content(self, prompt: str, mime_type: str, file_uri: str = None, audio_content: bytes = None) -> Dict[str, Any]:
        """
        Call Gemini generateContent with a file URI or inline data and a prompt.
        Expects JSON output from the model.
        Returns: {"data": parsed_json, "thought": thoughts_string}
        """
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        if self.use_inline_data and audio_content:
            audio_part = {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(audio_content).decode("utf-8")
                }
            }
        else:
            audio_part = {
                "file_data": {
                    "mime_type": mime_type,
                    "file_uri": file_uri
                }
            }
        
        payload = {
            "generationConfig": {
                "response_mime_type": "application/json",
                "thinking_config": {
                    "include_thoughts": True,
                    "thinking_level": self.thinking_level
                }
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        audio_part
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            for attempt in range(3):
                resp = await client.post(url, json=payload)
                if resp.status_code == 503 and attempt < 2:
                    await asyncio.sleep(5)
                    continue
                if resp.status_code >= 400:
                    print(f"Error generating content: {resp.status_code} - {resp.text}")
                resp.raise_for_status()
                break
            
            result = resp.json()
            
            # Extract thoughts and text
            parts = result["candidates"][0]["content"]["parts"]
            thoughts = []
            text_parts = []
            
            for part in parts:
                if part.get("thought"):
                    thoughts.append(part.get("text", ""))
                else:
                    text_parts.append(part.get("text", ""))
            
            full_thoughts = "\n".join(thoughts)
            text_response = "".join(text_parts)
            
            if full_thoughts:
                print(f"\n--- Model Thought Process ---\n{full_thoughts}\n-----------------------------\n")
            
            parsed_data = None
            try:
                parsed_data = json.loads(text_response)
            except json.JSONDecodeError:
                # Try to clean up markdown blocks if present
                import re
                json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text_response, re.DOTALL)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                
                if parsed_data is None:
                    # Last resort fallback if still fails
                    try:
                        start = text_response.find('[') if text_response.find('[') != -1 else text_response.find('{')
                        end = text_response.rfind(']') if text_response.rfind(']') != -1 else text_response.rfind('}')
                        if start != -1 and end != -1:
                            parsed_data = json.loads(text_response[start:end+1])
                    except json.JSONDecodeError:
                        pass
            
            if parsed_data is None:
                parsed_data = text_response
                
            return {"data": parsed_data, "thought": full_thoughts}
