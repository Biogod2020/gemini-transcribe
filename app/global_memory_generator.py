from typing import Dict, Any
from app.gemini_client import GeminiClient

class GlobalMemoryGenerator:
    def __init__(self, client: GeminiClient):
        self.client = client
        self.prompt = (
            "请完整听完这段音频。请输出一个严格的 JSON 格式数据，包含三个字段：\n"
            "1. 'theme': 概括核心议题（50字内）。\n"
            "2. 'speakers': 数组，列出所有出现的不同说话人，包含 'id' (如 Speaker_A) 和 'characteristics' (声音特征和身份推测)。\n"
            "3. 'glossary': 数组，列出 10-20 个核心的专有名词或行业术语。"
        )

    async def generate(self, audio_content: bytes, display_name: str = "full_audio") -> Dict[str, Any]:
        """
        Orchestrates the global memory generation process.
        """
        # 1. Upload the full audio
        file_uri, file_name = await self.client.upload_file(
            audio_content, 
            mime_type="audio/mpeg", 
            display_name=display_name
        )
        
        # 2. Wait for the file to be processed
        is_ready = await self.client.poll_file_state(file_name)
        if not is_ready:
            raise RuntimeError(f"File {file_name} failed to become ACTIVE.")
            
        # 3. Generate the global context JSON
        memory = await self.client.generate_content(
            prompt=self.prompt,
            file_uri=file_uri,
            mime_type="audio/mpeg"
        )
        
        return memory
