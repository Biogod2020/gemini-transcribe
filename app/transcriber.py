import json
import re
from typing import Dict, Any, List

def build_transcription_prompt(global_memory: Dict[str, Any], processed_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds the sliding window transcription prompt containing global memory and N-2 local context.
    Ensures that only the last 2 chunks are used for context.
    """
    theme = global_memory.get("theme", "")
    glossary = ", ".join(global_memory.get("glossary", []))
    speakers = json.dumps(global_memory.get("speakers", []), ensure_ascii=False)
    
    # Get the last two processed chunks for sliding window context
    # This is the core logic for N-2 context
    context_chunks = processed_chunks[-2:] if len(processed_chunks) >= 2 else processed_chunks
    
    context_text = ""
    if len(context_chunks) == 2:
        context_text = (
            f"【近期历史转录（仅供参考对齐，切勿重复转写）】\n"
            f"倒数第二段：{context_chunks[0].get('transcript', '')}\n"
            f"上一段：{context_chunks[1].get('transcript', '')}"
        )
    elif len(context_chunks) == 1:
        context_text = (
            f"【近期历史转录（仅供参考对齐，切勿重复转写）】\n"
            f"上一段：{context_chunks[0].get('transcript', '')}"
        )
    else:
        context_text = "【近期历史转录】\n（这是第一段音频，无历史转录）"

    prompt = f"""【系统级全局记忆】
核心议题：{theme}
专有名词表：{glossary}
说话人画像：{speakers}

{context_text}

【当前任务】
请紧接“上一段”的结尾（如果有的话），逐字转写本次音频流。严格使用【全局记忆】中的说话人 id。

请输出 JSON 格式的数组，每个元素包含 'speaker_id' 和 'text' 两个字段。
示例：
[
  {{"speaker_id": "SPEAKER_01", "text": "你好，今天我们讨论一下..."}},
  {{"speaker_id": "SPEAKER_02", "text": "好的，我先开始。"}}
]"""

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
