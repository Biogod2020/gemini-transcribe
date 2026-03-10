import json
import re
from typing import Dict, Any, List

def build_transcription_prompt(global_memory: Dict[str, Any], processed_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds the transcription prompt containing global memory and ALL previous local context.
    Instructs the model to use Chain-of-Thought reasoning.
    """
    theme = global_memory.get("theme", "")
    glossary = ", ".join(global_memory.get("glossary", []))
    speakers = json.dumps(global_memory.get("speakers", []), ensure_ascii=False)
    
    context_text = ""
    if processed_chunks:
        context_text = "【历史转录全文（仅供参考对齐上下文，切勿重复转写）】\n"
        for chunk in processed_chunks:
            context_text += f"--- 第 {chunk['chunk_index']} 段 ---\n{chunk.get('transcript', '')}\n"
    else:
        context_text = "【历史转录全文】\n（这是第一段音频，无历史转录）"

    prompt = f"""【系统级全局记忆】
核心议题：{theme}
专有名词表：{glossary}
说话人画像：{speakers}

{context_text}

【当前任务】
请紧接上一段的结尾（如果有的话），转写本次音频流。
在进行转写前，请先进行一步一步的思考和分析（Chain-of-Thought）：
1. 结合【系统级全局记忆】和【历史转录全文】的逻辑，理解当前音频段落的上下文和语境。
2. 识别当前说话人的意图，确保对话逻辑连贯，不要生硬地字对字直译，而要根据逻辑理顺内容，但必须忠于原意。
3. 严格使用【系统级全局记忆】中的说话人 id。

请在思考结束后，输出 JSON 格式的数组，每个元素包含 'speaker_id' 和 'text' 两个字段。
示例输出结构：
首先，根据上文的语境...这段音频主要讨论...
```json
[
  {{"speaker_id": "SPEAKER_01", "text": "你好，今天我们讨论一下..."}},
  {{"speaker_id": "SPEAKER_02", "text": "好的，我先开始。"}}
]
```"""

    return prompt

def parse_transcription_response(response: str) -> List[Dict[str, str]]:
    """
    Parses the JSON transcription result from Gemini, handling Markdown code blocks.
    """
    # Try to extract JSON from markdown code blocks if present
    json_match = re.search(r"```(?:json)?\s*(.*?)```", response, re.DOTALL)
    if json_match:
        response = json_match.group(1).strip()
    else:
        # Fallback: find the first '[' and last ']'
        start = response.find('[')
        end = response.rfind(']')
        if start != -1 and end != -1:
            response = response[start:end+1]
    
    try:
        data = json.loads(response)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        # If still fails, try some basic cleanup (like trailing commas)
        try:
            # Very aggressive cleanup could go here, but for now just return empty
            return []
        except:
            return []
