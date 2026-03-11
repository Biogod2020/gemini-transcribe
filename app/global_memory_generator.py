from typing import Dict, Any
from app.gemini_client import GeminiClient

class GlobalMemoryGenerator:
    def __init__(self, client: GeminiClient):
        self.client = client
        self.prompt = (
            "请完整听完这段音频，并进行深度的全局语义分析。你的目标是为后续的分段转录提供核心上下文参考。\n"
            "请输出一个严格的 JSON 格式数据，包含以下六个字段：\n"
            "1. 'theme': 核心议题的高度概括（50字内）。\n"
            "2. 'speakers': 数组，识别所有出现的不同说话人，包含 'id'（唯一标识符）和 'characteristics'（基于声学特征、语气和谈话内容的身份推测）。\n"
            "3. 'glossary': 数组，提取音频中出现的 10-20 个核心专有名词、行业术语或高频关键词。\n"
            "4. 'tone': 概括音频的总体情感基调与交互氛围。\n"
            "5. 'key_decisions': 数组，记录音频中明确达成的关键共识、决策或结论（若无则为空）。\n"
            "6. 'narrative_structure': 描述音频的整体逻辑流向或议程结构。"
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
        
        # 2. Wait for the file to be processed (if not using inline data)
        is_ready = await self.client.poll_file_state(file_name)
        if not is_ready:
            raise RuntimeError(f"File {file_name} failed to become ACTIVE.")
            
        # 3. Generate the global context JSON
        # The client will handle printing thoughts if Thinking Mode is active.
        response = await self.client.generate_content(
            prompt=self.prompt,
            mime_type="audio/mpeg",
            file_uri=file_uri,
            audio_content=audio_content
        )
        
        return response["data"]
