import json
import asyncio
import httpx
import base64
from typing import Tuple, Dict, Any
from app.config import config

from app.models import (
    GenerateContentRequest, GenerationConfig, ThinkingConfig, 
    Content, Part, InlineData, FileData
)

from app.utils import extract_content_and_thoughts

class GeminiClient:
    def __init__(self, api_key: str = config.API_KEY, model: str = config.DEFAULT_MODEL, use_inline_data: bool = config.USE_INLINE_DATA, thinking_level: str = config.THINKING_LEVEL):
        self.api_key = api_key
        self.model = model
        self.base_url = config.BASE_URL
        self.upload_url = config.UPLOAD_URL
        self.use_inline_data = use_inline_data
        self.thinking_level = thinking_level
        # Auto-detect local proxy
        self.is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url

    async def upload_file(self, content: bytes, mime_type: str, display_name: str) -> Tuple[str, str]:
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

    async def generate_content(self, prompt: str, mime_type: str, file_uri: str = None, audio_content: bytes = None, response_schema: Any = None) -> Dict[str, Any]:
        """
        Call Gemini generateContent with a file URI or inline data and a prompt.
        Handles native thinking and structured output.
        Returns: {"data": parsed_json, "thought": thoughts_string}
        """
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        parts = [Part(text=prompt)]
        
        if self.use_inline_data and audio_content:
            parts.append(Part(inline_data=InlineData(
                mimeType=mime_type,
                data=base64.b64encode(audio_content).decode("utf-8")
            )))
        elif file_uri:
            parts.append(Part(file_data=FileData(
                mimeType=mime_type,
                fileUri=file_uri
            )))
        
        # Consistent snake_case for thinking_config as required by Gemini 3.x v1beta (official & local)
        thinking_config = ThinkingConfig(
            include_thoughts=True,
            thinking_level=self.thinking_level,
            thinking_budget=None # Omit budget when level is provided
        )
        
        gen_config = GenerationConfig(
            responseMimeType="application/json",
            responseSchema=response_schema,
            thinking_config=thinking_config
        )

        request = GenerateContentRequest(
            contents=[Content(role="user", parts=parts)],
            generationConfig=gen_config
        )
        
        # Official Gemini 3.x v1beta seems to expect snake_case for these new fields
        # while existing fields like responseMimeType work in both.
        # request.model_dump(by_alias=False) gives us snake_case.
        payload = request.model_dump(by_alias=False, exclude_none=True)
        
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
            extracted = extract_content_and_thoughts(result)
            
            if extracted["thought"]:
                print(f"\n--- Model Thought Process ---\n{extracted['thought']}\n-----------------------------\n")
                
            return extracted
