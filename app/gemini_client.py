import json
import asyncio
import httpx
from typing import Tuple, Dict, Any

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
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
            # 1. Start the resumable upload
            resp = await client.post(
                f"{self.upload_url}?key={self.api_key}",
                headers=headers,
                json=metadata
            )
            resp.raise_for_status()
            upload_url = resp.headers["X-Goog-Upload-URL"]
            
            # 2. Upload the actual file content
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
        url = f"{self.base_url}/models/gemini-3.0-flash-preview:generateContent?key={self.api_key}"
        
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
            return json.loads(text_response)
