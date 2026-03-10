import json
import re
from typing import Dict, Any, List

def build_transcription_prompt(global_memory: Dict[str, Any], processed_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds a SOTA-level transcription prompt that is domain-agnostic and relies on internal reasoning.
    """
    if isinstance(global_memory, list) and len(global_memory) > 0:
        global_memory = global_memory[0]
        
    theme = global_memory.get("theme", "")
    glossary = ", ".join(global_memory.get("glossary", []))
    speakers = json.dumps(global_memory.get("speakers", []), ensure_ascii=False)
    
    context_text = ""
    if processed_chunks:
        context_text = "## 历史对齐上下文 (仅供参考衔接)\n"
        for chunk in processed_chunks:
            context_text += f"--- 第 {chunk['chunk_index']} 段 ---\n{chunk.get('transcript', '')}\n"
    else:
        context_text = "（这是音频的第一部分，尚无历史转录参考）"

    prompt = f"""# 角色：专业多语种语音转录与语义对齐专家

## 1. 核心任务
你的任务是根据提供的音频片段，输出高准确度的逐字稿。你必须利用提供的“全局记忆”和“历史上下文”来确保术语一致、说话人标识准确且逻辑连贯。

## 2. 基础参考信息
- **全局核心议题**：{theme}
- **术语/实体定义**：{glossary}
- **说话人画像参考**：{speakers}

## 3. 上下文衔接参考
{context_text}

## 4. 转录理解准则 (SOTA Guidelines)
- **语义锚定**：充分利用历史上下文来消解当前音频中的代词指向、话题跳跃和专有名词。
- **声学鲁棒性**：针对含糊不清、带口音或含噪音的语音，必须结合语义逻辑和“全局核心议题”进行合理的上下文推断，严禁生拼硬造不符合逻辑的词汇。
- **语流规范化**：在忠实于原意的前提下，确保转录文本符合人类表达的句法逻辑，消除因语音断断续续导致的语法破碎感。
- **标识持久化**：严格遵循说话人画像中的 ID。严禁在同一段对话中随意更改同一说话人的标识。

## 5. 输出约束
- **格式要求**：必须输出一个且仅输出一个 JSON 格式的数组。
- **结构定义**：数组中的每个对象必须包含 `speaker_id` 和 `text` 字段。
- **逻辑隔离**：不要在 JSON 之外包含任何解释、前言或总结。所有推理逻辑应当在模型的内部思考环节（Reasoning Phase）完成。

请紧接前文，开始当前片段的转录：
```json
[
  {{"speaker_id": "SPEAKER_ID", "text": "转写内容..."}}
]
```"""

    return prompt

def parse_transcription_response(response: str) -> List[Dict[str, str]]:
    """
    Robustly parses the JSON array from the model's response.
    This is now a secondary fallback since GeminiClient handles the primary parsing.
    """
    # 1. Try direct JSON parse
    try:
        data = json.loads(response)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # 2. Try to find JSON block via regex
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Last ditch attempt: find the outer brackets
    start = response.find('[')
    end = response.rfind(']')
    if start != -1 and end != -1:
        try:
            return json.loads(response[start:end+1])
        except json.JSONDecodeError:
            pass

    return []
