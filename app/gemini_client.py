import json
import asyncio
import httpx
import base64
import os
import time
import random
from typing import Tuple, Dict, Any, Optional, Union
from app.config import config

from app.models import (
    GenerateContentRequest, GenerationConfig, ThinkingConfig, 
    Content, Part, InlineData, FileData
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
            # Auto-detect local proxy
            self.is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
            # Smart Adaptation: Force inline_data for local proxy
            if use_inline_data is not None:
                self.use_inline_data = use_inline_data
            else:
                self.use_inline_data = True if self.is_local else config.USE_INLINE_DATA
            
            if self.is_local:
                print(f">>> GeminiClient: Local proxy detected ({self.base_url}). Auto-switching to INLINE_DATA mode.")

        self.upload_url = f"{self.base_url.replace('/v1beta', '/upload/v1beta')}/files" if not self.is_local else self.base_url
        self.thinking_level = thinking_level or config.THINKING_LEVEL

    async def upload_file(self, source: Union[bytes, str], mime_type: str, display_name: str) -> Tuple[str, str]:
        """
        Uploads a file using resumable protocol. Supports both raw bytes and file paths.
        """
        if self.use_inline_data:
            return "inline_mode", "inline_mode"

        if isinstance(source, str):
            file_size = os.path.getsize(source)
            def get_content():
                with open(source, "rb") as f: return f.read()
            content = await asyncio.to_thread(get_content)
        else:
            file_size = len(source)
            content = source
            
        headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(file_size),
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
                    "Content-Length": str(file_size)
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

    async def generate_content(self, prompt: str, mime_type: str, file_uri: str = None, audio_content: Optional[bytes] = None, response_schema: Any = None) -> Dict[str, Any]:
        """
        Call Gemini generateContent with exponential backoff and jitter.
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
        
        thinking_config = ThinkingConfig(
            include_thoughts=True,
            thinking_level=self.thinking_level,
            thinking_budget=None
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
        
        payload = request.model_dump(by_alias=True, exclude_none=True)
        if "generationConfig" in payload and "thinkingConfig" in payload["generationConfig"]:
            tc = payload["generationConfig"].pop("thinkingConfig")
            payload["generationConfig"]["thinking_config"] = {
                "include_thoughts": tc.get("include_thoughts", True),
                "thinking_level": tc.get("thinking_level") or tc.get("thinkingLevel"),
                "thinking_budget": tc.get("thinking_budget") or tc.get("thinkingBudget")
            }
        
        payload_size_mb = len(json.dumps(payload)) / (1024 * 1024)
        print(f">>> GeminiClient: Sending request ({payload_size_mb:.2f} MB payload)...")
        
        start_time_req = time.time()
        max_attempts = 6
        async with httpx.AsyncClient(timeout=600.0) as client:
            for attempt in range(max_attempts):
                try:
                    resp = await client.post(url, json=payload)
                    
                    if resp.status_code in [429, 503] and attempt < max_attempts - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after and retry_after.isdigit():
                            wait_time = max(wait_time, int(retry_after))
                        
                        print(f">>> GeminiClient: {resp.status_code} error, retrying {attempt+1}/{max_attempts} in {wait_time:.2f}s...")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    if resp.status_code >= 400:
                        print(f"Error generating content: {resp.status_code} - {resp.text}")
                    resp.raise_for_status()
                    break
                except Exception as e:
                    if attempt == max_attempts - 1: raise e
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f">>> GeminiClient: Request attempt {attempt+1} failed: {e}. Retrying in {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
            
            req_duration = time.time() - start_time_req
            print(f">>> GeminiClient: Response received in {req_duration:.2f}s.")
            result = resp.json()
            extracted = extract_content_and_thoughts(result)
            
            if extracted["thought"]:
                print(f"\n--- Model Thought Process ---\n{extracted['thought']}\n-----------------------------\n")
                
            return extracted
