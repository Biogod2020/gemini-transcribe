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
        
        thinking_config = ThinkingConfig(
            includeProcess=True,
            thinkingLevel=self.thinking_level
        )
        
        gen_config = GenerationConfig(
            responseMimeType="application/json",
            responseSchema=response_schema,
            thinkingConfig=thinking_config
        )

        request = GenerateContentRequest(
            contents=[Content(role="user", parts=parts)],
            generationConfig=gen_config
        )
        
        payload = request.model_dump(by_alias=True, exclude_none=True)
        
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
            
            # Extract thoughts and text (Refined logic based on official API behavior)
            candidates = result.get("candidates", [])
            if not candidates:
                return {"data": [], "thought": "No candidates returned"}
                
            parts_resp = candidates[0].get("content", {}).get("parts", [])
            thoughts = []
            text_parts = []
            
            for part in parts_resp:
                part_text = part.get("text", "")
                # Official API uses the 'thought' boolean flag
                if part.get("thought"):
                    thoughts.append(part_text)
                else:
                    text_parts.append(part_text)
            
            full_thoughts = "\n".join(thoughts).strip()
            text_response = "".join(text_parts).strip()
            
            # Print thoughts for real-time logging
            if full_thoughts:
                print(f"\n--- Model Thought Process ---\n{full_thoughts}\n-----------------------------\n")
            
            # Parse the final JSON response
            parsed_data = None
            try:
                parsed_data = json.loads(text_response)
            except json.JSONDecodeError:
                # Robust extraction if the model still surrounds JSON with text/markdown
                import re
                json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text_response, re.DOTALL)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                
                if parsed_data is None:
                    # Last resort: find outer brackets
                    start = text_response.find('[') if text_response.find('[') != -1 else text_response.find('{')
                    end = text_response.rfind(']') if text_response.rfind(']') != -1 else text_response.rfind('}')
                    if start != -1 and end != -1:
                        try:
                            parsed_data = json.loads(text_response[start:end+1])
                        except json.JSONDecodeError:
                            pass
            
            if parsed_data is None:
                parsed_data = text_response # Fallback to raw text if parsing impossible
                
            return {"data": parsed_data, "thought": full_thoughts}

