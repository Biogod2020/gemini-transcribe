# Initial Concept

这份详细的工程级项目设计书（Technical Specification）为你量身定制。我将非结构化的概念完全转化为**结构化的数据字典、具体的 RESTful API 报文格式，以及精确的状态机流转逻辑**，确保任何一位有经验的后端工程师拿到这份文档后，能够零歧义地直接开始编码。

---

# 🚀 高精度长音频 STT Agent (MVP 版本) 工程设计说明书

## 1. 系统概述与核心基准

* **目标：** 实现超长音频的高精度、带说话人分离的逐字转录，解决上下文断裂和人物指代混乱问题。
* **核心模型：** `gemini-3.1-flash-lite-preview`（用于所有语言理解和转写任务）。
* **交互方式：** 纯原生 HTTP RESTful API（无任何官方 SDK 封装）。
* **音频预处理：** 本地 CPU 运行的轻量级 VAD（Voice Activity Detection）模型。

---

## 2. 核心状态机设计 (State Management)

系统在运行生命周期中，工程师需要在内存/数据库中维护一个核心的 State 对象。这是整个“双层记忆”的具象化体现。

```json
// 系统运行时的内存状态 (State Object)
{
  "project_id": "audio_task_001",
  "global_memory": {
    "theme": "",             // 音频核心议题
    "glossary": [],          // 专有名词表 (Array of Strings)
    "speakers": []           // 说话人画像 (Array of Objects: {id, characteristics})
  },
  "processed_chunks": [
    // 存放按顺序处理完成的切片转写结果
    // { "chunk_index": 1, "transcript": "Speaker_A: 大家好..." }
  ]
}

```

---

## 3. 模块化执行流程与接口定义

### 模块一：本地 VAD 物理切片 (Local Segmentation)

* **执行逻辑：**
1. 输入完整 `source_audio.mp3`。
2. 加载轻量级 VAD 模型（如 Silero VAD，纯 CPU 运行）。
3. 以 7-10 分钟为目标边界，寻找最接近该长度且 VAD 置信度 `< 0.1` 持续时长 `> 700ms` 的静音点进行切割。


* **输出约定：** 生成一系列按序命名的文件：`chunk_1.mp3`, `chunk_2.mp3` ... `chunk_N.mp3`。

### 模块二：构建全局记忆 (Global Context Initialization)

* **前置动作：** 使用 Google File API 上传**完整未切割的原始音频**，获取到文件的 `fileUri`。
* **API 请求：** 生成全局记忆
* **Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={{API_KEY}}`
* **Headers:** `Content-Type: application/json`
* **Payload (请求体):**
```json
{
  "generationConfig": {
    "response_mime_type": "application/json"
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "请完整听完这段音频。请进行深度的全局分析，并输出一个严格的 JSON 格式数据，包含以下六个字段：\n1. 'theme': 概括核心议题（50字内）。\n2. 'speakers': 数组，列出所有出现的不同说话人，包含 'id' (如 Speaker_A) 和 'characteristics' (声音特征和身份推测)。\n3. 'glossary': 数组，列出 10-20 个核心的专有名词或行业术语。\n4. 'tone': 字符串，概括整段音频的总体基调和氛围。\n5. 'key_decisions': 数组，列出音频中达成的关键共识或重要决定。\n6. 'narrative_structure': 字符串，简述音频的整体叙事结构或会议议程。"
        },
        {
          "fileData": {
            "mimeType": "audio/mp3",
            "fileUri": "填入完整长音频的 fileUri"
          }
        }
      ]
    }
  ]
}

```




* **工程师动作：** 将 API 响应的 JSON 解析后，全量赋值给系统状态机中的 `State.global_memory`。

### 模块三：核心全量上下文转写循环 (Full-Context Loop)

* **执行逻辑：** 对模块一生成的 `chunk_1` 到 `chunk_N` 进行一个 `for` 循环遍历。假设当前处理到 `chunk_i`。
* **前置动作：** 上传当前的 `chunk_i.mp3`，获取其 `fileUri`。
* **上下文提取：**
* 提取完整历史：`full_context = State.processed_chunks`（拼接为带段落号的长文本，如果为空则提示无历史）。

* **API 请求：** 精准转写 (带 Chain-of-Thought)
* **Endpoint:** 同模块二。
* **Payload (请求体 - 请工程师通过代码动态拼接):**
```json
{
  "generationConfig": {
    "response_mime_type": "application/json"
  },
  "system_instruction": {
    "parts": [
      {
        "text": "你是一个严谨的语音转写专家。你必须忠实转录提供的音频，但需要根据语境理顺逻辑。"
      }
    ]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "【系统级全局记忆】\n核心议题：{{State.global_memory.theme}}\n专有名词表：{{State.global_memory.glossary}}\n说话人画像：{{State.global_memory.speakers}}\n\n【历史转录全文（仅供参考对齐上下文，切勿重复转写）】\n{{full_context}}\n\n【当前任务】\n请紧接上一段的结尾转写。在进行转写前，请先进行一步一步的思考和分析（Chain-of-Thought），理顺逻辑和意图。思考结束后，输出 JSON 数组，每个元素包含 'speaker_id' 和 'text' 两个字段。"
        },
        {
          "fileData": {
            "mimeType": "audio/mp3",
            "fileUri": "填入当前 chunk_i 的 fileUri"
          }
        }
      ]
    }
  ]
}

```

* **工程师动作：**
1. 解析大模型返回的 JSON（忽略前面的思考过程文本）。
2. 将数组格式化为纯文本格式（例如 `"Speaker_A: 刚刚说到的..."`）。
3. 将格式化后的完整字符串 push 到 `State.processed_chunks` 数组中。
4. 循环进入下一个 Chunk。



### 模块四：数据组装与导出 (Export)

* **执行逻辑：** 当循环结束，所有的切片转写都已存在于 `State.processed_chunks` 中。
* **工程师动作：**
1. 按照 `chunk_index` 顺序，将所有的 `transcript` 字符串用换行符 `\n\n` 拼接起来。
2. （可选优化）遍历 `State.global_memory.speakers`，如果后续确定了某人的真实姓名，可以在最终的纯文本中进行一次全局的 `String.replace("Speaker_A", "真实的姓名")`。
3. 导出为 Markdown 或 TXT 交付文件。



---

## 4. 工程师避坑指南 (Critical Notes for Devs)

1. **文件 URI 有效期：** Google File API 上传的 `fileUri` 默认有 48 小时的生命周期，且对于大文件，上传后可能需要轮询检查 `state === 'ACTIVE'` 才能用于推理（通常在几秒内就绪）。
2. **强制 JSON 输出：** 模块二 and 模块三都在 Payload 中明确设置了 `response_mime_type: "application/json"`。这能极大降低工程师写正则表达式解析文本的痛苦，确保数据结构化流转。
3. **速率控制：** API 请求之间必须做好 `await`，因为后一个 Chunk 的转写强依赖于前两个 Chunk 的输出结果。如果遇到 HTTP 429 报错，请实现指数退避（Exponential Backoff）重试机制。

---

# Product Guide: High-Precision Long Audio STT Agent (MVP)

## Vision
An AI-driven speech-to-text (STT) agent that provides ultra-accurate, speaker-aware, and context-aligned transcriptions for long-form audio. By leveraging dual-layer memory (global and local) and sliding window processing, the agent eliminates context fragmentation and speaker identification errors common in traditional STT solutions.

## Target Audience
- **General Users**: Anyone requiring professional-grade transcription for long audio files (e.g., meetings, interviews, lectures).

## Core Features (MVP)
1. **High-Precision Transcription**: Using `gemini-3.1-flash-lite-preview` to achieve verbatim accuracy without summarization or creative rewriting.
2. **Speaker Consistency & Diarization**: Global speaker profiling ensures consistent identity across long recordings, even when audio is chunked.
3. **Glossary-Aware Alignment**: A pre-generated global glossary ensures specialized terminology and proper nouns are transcribed correctly throughout the document.
4. **Local VAD-Based Segmentation**: Intelligent audio splitting at silence points using Voice Activity Detection (VAD) to maintain natural speech flow.
5. **Dual-Layer Contextual Memory**:
   - **Global Memory**: High-level overview, speaker profiles, and glossary.
   - **Local Memory**: Full history context injection to ensure seamless transitions and logical flow across chunks.

## Technical Architecture
- **Environment**: Web-based application.
- **Processing**: Local CPU-based VAD for initial segmentation.
- **AI Backend**: Direct HTTP RESTful API calls to Google's Generative Language API (Gemini).
- **Storage/State**: Memory/Database-backed state machine for managing audio chunks and transcription flow.

## Output & Integrations
- **Supported Formats**: Structured JSON for programmatic consumption and downstream processing.
- **Interface**: RESTful API for integration into wider web ecosystems.
