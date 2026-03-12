import asyncio
import json
from typing import List, Dict, Any
from app.gemini_client import GeminiClient

class GlobalMemoryGenerator:
    def __init__(self, client: GeminiClient):
        self.client = client
        
        # --- SOTA Prompt: Single Pass (Direct) ---
        self.single_pass_prompt = (
            "你是一个顶级的多模态理解专家。你面前的是一段超长音频的完整流。你的目标是进行深度的全局语义解构。\n"
            "在输出最终 JSON 前，请先进行 Chain-of-Thought 分析：理清叙事脉络、参与者立场演变以及隐含的核心议题。\n"
            "请输出严格的 JSON 数据，包含以下六个字段：\n"
            "1. 'theme': 核心议题的高度概括与底层逻辑（50字内）。\n"
            "2. 'speakers': 数组，包含 'id' 和 'characteristics'（基于声学特征、语气及行为逻辑的画像）。\n"
            "3. 'glossary': 数组，提取音频中具有行业背景或特定语境含义的专有名词。\n"
            "4. 'tone': 描述音频的总体情感基调、交互氛围及其细微变化。\n"
            "5. 'key_decisions': 数组，记录音频中明确达成或隐含的关键共识、结论及下一步行动。\n"
            "6. 'narrative_structure': 描述音频的整体逻辑骨架或议程推进过程。"
        )

        # --- SOTA Prompt: Map Phase ---
        self.map_prompt_template = (
            "你是一个精密的审计分析师。你正在听整段超长音频的第 {idx} 个分块（带重叠）。\n"
            "你的任务是为后续的全局聚合提供高保真的碎片化信息。请聚焦于：\n"
            "1. 本片段独有的核心讨论点与事实。\n"
            "2. 出现的说话人、他们的具体观点、语气及其身份暗示。\n"
            "3. 提到的关键术语、决策碎片或重要结论。\n"
            "请保持输出的客观性与解构性，为最终的架构师聚合提供最佳原材料。"
        )

        # --- SOTA Prompt: Reduce Phase ---
        self.reduce_prompt_template = (
            "你是一个高级系统架构师。你的输入是来自多个片段审计师对同一场会议不同时间段的精细报告。\n"
            "报告列表如下：\n"
            "--------------------------\n"
            "{segment_summaries}\n"
            "--------------------------\n"
            "你的任务是将这些碎片化、重叠的信息，通过“逻辑去重”与“语义对齐”，合成一份终极的全局语义图谱 JSON：\n"
            "1. 'theme': 综合各片段，提炼核心议题的演进与最终定论。\n"
            "2. 'speakers': 跨片段识别并合并同一说话人，提供完整的特征画像。\n"
            "3. 'glossary': 汇总并统一解释全局出现的行业黑话与专业术语。\n"
            "4. 'tone': 概括整段音频的总体情感基调演变。\n"
            "5. 'key_decisions': 将各片段的决策碎片串联为完整的决策链条。\n"
            "6. 'narrative_structure': 还原整段音频的宏观叙事结构或会议完整议程。"
        )

    async def _process_single_chunk(self, file_path: str, idx: int) -> Dict[str, Any]:
        """
        Map Phase: Extract high-fidelity segment info.
        """
        print(f"Map Phase -> Processing chunk {idx}...")
        with open(file_path, "rb") as f:
            content = f.read()
            
        file_uri, file_name = await self.client.upload_file(
            content, mime_type="audio/wav", display_name=f"map_chunk_{idx}"
        )
        
        if not await self.client.poll_file_state(file_name):
            raise RuntimeError(f"Chunk {idx} failed to become ACTIVE.")
            
        response = await self.client.generate_content(
            prompt=self.map_prompt_template.format(idx=idx),
            mime_type="audio/wav",
            file_uri=file_uri
        )
        return response

    async def generate(self, source: Any) -> Dict[str, Any]:
        """
        Smart dispatcher: Choose Single-Pass or Map-Reduce based on input type.
        """
        # If source is a list of paths, use Map-Reduce
        if isinstance(source, list):
            print(f"🚀 Initializing Map-Reduce Pipeline for {len(source)} chunks...")
            
            # 1. Map Phase
            tasks = [self._process_single_chunk(path, i+1) for i, path in enumerate(source)]
            chunk_results = await asyncio.gather(*tasks)
            
            # 2. Reduce Phase
            print("\n🏁 Map Phase Complete. Initializing Reduce Phase Aggregation...")
            segment_summaries = ""
            for i, res in enumerate(chunk_results):
                text = str(res.get("data", res.get("text", "")))
                segment_summaries += f"\n[Auditor Report - Segment {i+1}]:\n{text}\n"
                
            reduce_prompt = self.reduce_prompt_template.format(segment_summaries=segment_summaries)
            final_response = await self.client.generate_content(
                prompt=reduce_prompt,
                mime_type="text/plain"
            )
            return final_response["data"]

        # If source is bytes, use Single-Pass
        else:
            print("🚀 Initializing Single-Pass Direct Summary...")
            file_uri, file_name = await self.client.upload_file(
                source, mime_type="audio/wav", display_name="single_pass_summary"
            )
            if not await self.client.poll_file_state(file_name):
                raise RuntimeError("File upload failed for single-pass.")
                
            response = await self.client.generate_content(
                prompt=self.single_pass_prompt,
                mime_type="audio/wav",
                file_uri=file_uri,
                audio_content=source if self.client.use_inline_data else None
            )
            return response["data"]
