import json
import asyncio
import httpx
import base64
import os
import time
from typing import Tuple, Dict, Any, Optional
from app.config import config

from app.models import (
    GenerateContentRequest, GenerationConfig, ThinkingConfig, 
    Content, Part, FileData
)
from app.utils import extract_content_and_thoughts

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = None, use_inline_data: bool = None, thinking_level: str = None, base_url: str = None):
        self.model = model or config.DEFAULT_MODEL
        
        # Hard-route for 3.1 Flash Lite (Official only)
        self.is_lite_31 = "gemini-3.1-flash-lite-preview" in self.model
        
        if self.is_lite_31:
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.api_key = os.environ.get("GEMINI_API_KEY") or config.API_KEY
            self.use_inline_data = use_inline_data if use_inline_data is not None else config.USE_INLINE_DATA
            self.is_local = False
            print(f">>> GeminiClient: Model {self.model} forced to OFFICIAL API.")
        else:
            self.base_url = base_url or config.BASE_URL
            self.api_key = api_key or config.API_KEY
            self.is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
            
            if use_inline_data is not None:
                self.use_inline_data = use_inline_data
            else:
                self.use_inline_data = True if self.is_local else config.USE_INLINE_DATA
            
            if self.is_local:
                print(f">>> GeminiClient: Local proxy detected ({self.base_url}). Auto-switching to INLINE_DATA mode.")

        self.upload_url = f"{self.base_url.replace('/v1beta', '/upload/v1beta')}/files" if not self.is_local else self.base_url
        self.thinking_level = thinking_level or config.THINKING_LEVEL

    async def upload_file(self, content: bytes, mime_type: str, display_name: str) -> Tuple[str, str]:
        if self.use_inline_data:
            return "inline_mode", "inline_mode"
            
        headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(len(content)),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient() as client:
            # 1. Start session
            resp = await client.post(
                f"{self.upload_url}?key={self.api_key}",
                headers=headers,
                json={"file": {"display_name": display_name}}
            )
            resp.raise_for_status()
            upload_url = resp.headers["X-Goog-Upload-URL"]

            # 2. Upload content
            resp = await client.put(
                upload_url,
                headers={"X-Goog-Upload-Command": "upload, finalize", "X-Goog-Upload-Offset": "0"},
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
                if resp.status_code == 200:
                    state = resp.json().get("state")
                    if state == "ACTIVE":
                        return True
                    if state == "FAILED":
                        return False
                await asyncio.sleep(interval)
        return False

    async def generate_content(self, prompt: str, mime_type: str, file_uri: str = None, audio_content: bytes = None, response_schema: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        parts = [Part(text=prompt)]
        if self.use_inline_data and audio_content:
            parts.append(Part(inline_data=FileData(
                mimeType=mime_type,
                data=base64.b64encode(audio_content).decode("utf-8")
            )))
        elif file_uri:
            parts.append(Part(file_data=FileData(
                mimeType=mime_type,
                fileUri=file_uri
            )))
        
        generation_config = GenerationConfig(
            response_mime_type="application/json" if response_schema else "text/plain",
            response_schema=response_schema
        )
        
        tc = ThinkingConfig.get_level(self.thinking_level)
        payload = GenerateContentRequest(
            contents=[Content(parts=parts, role="user")],
            generation_config=generation_config,
            thinking_config=ThinkingConfig(
                include_thoughts=tc.get("include_thoughts", True),
                include_thought=tc.get("include_thought", True)
            ) if self.thinking_level != "OFF" else None
        ).model_dump(by_alias=True, exclude_none=True)

        # --- Robust Retry Logic with Exponential Backoff ---
        max_attempts = 6
        backoff_factor = 2.0
        
        import time
        payload_size_mb = len(json.dumps(payload)) / (1024 * 1024)
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        wait_time = backoff_factor ** attempt
                        print(f">>> GeminiClient: Retrying in {wait_time:.1f}s (Attempt {attempt+1}/{max_attempts})...")
                        await asyncio.sleep(wait_time)
                    
                    if attempt == 0:
                        print(f">>> GeminiClient: Sending request ({payload_size_mb:.2f} MB payload)...")
                    
                    resp = await client.post(url, json=payload)
                    
                    if resp.status_code == 429:
                        print(f">>> GeminiClient: 429 Rate Limit hit.")
                        continue # Trigger backoff
                        
                    if resp.status_code == 503:
                        print(f">>> GeminiClient: 503 Overloaded.")
                        continue
                        
                    if resp.status_code >= 400:
                        print(f"Error generating content: {resp.status_code} - {resp.text}")
                        resp.raise_for_status()
                    
                    # Success
                    result = resp.json()
                    extracted = extract_content_and_thoughts(result)
                    
                    if extracted["thought"]:
                        print(f"\n--- Model Thought Process ---\n{extracted['thought'][:200]}...\n-----------------------------\n")
                        
                    return extracted
                    
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f">>> GeminiClient: Request failed: {e}. Retrying...")
        
        raise RuntimeError("Failed to generate content after maximum retries.")
