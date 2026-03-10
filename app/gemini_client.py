import json
import asyncio
import httpx
from typing import Tuple, Dict, Any

class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-3.1-flash-lite-preview"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.upload_url = "https://generativelanguage.googleapis.com/upload/v1beta/files"

    async def upload_file(self, content: bytes, mime_type: str, display_name: str) -> Tuple[str, str]:
        """
        Upload a file using the resumable upload protocol.
        Returns: (file_uri, file_name)
        """
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

    async def generate_content(self, prompt: str, file_uri: str, mime_type: str) -> Dict[str, Any]:
        """
        Call Gemini generateContent with a file URI and a prompt.
        Expects JSON output from the model.
        """
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "generationConfig": {
                "response_mime_type": "application/json"
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"file_data": {"mime_type": mime_type, "file_uri": file_uri}}
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            
            result = resp.json()
            text_response = result["candidates"][0]["content"]["parts"][0]["text"]
            try:
                return json.loads(text_response)
            except json.JSONDecodeError:
                # Try to clean up markdown blocks if present
                import re
                json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text_response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                # Last resort fallback if still fails
                try:
                    start = text_response.find('[') if text_response.find('[') != -1 else text_response.find('{')
                    end = text_response.rfind(']') if text_response.rfind(']') != -1 else text_response.rfind('}')
                    if start != -1 and end != -1:
                        return json.loads(text_response[start:end+1])
                except json.JSONDecodeError:
                    pass
                return text_response
