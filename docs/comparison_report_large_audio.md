# Large Audio STT Comparison Report: Gemini 3 Flash vs. Gemini 3.1 Flash Lite

## 1. Overview
This report documents the performance comparison between `gemini-3-flash-preview` (running via a local proxy with `include_thoughts`) and `gemini-3.1-flash-lite-preview` (running via the official Google Generative Language API with `inlineData` and `include_thoughts`). 

The test was conducted on a single merged audio file (`merged_full_audio.m4a`, approx. 57MB, ~1 hour duration), which consisted of 4 chronological segments concerning a field interview about "Puning Nanshan Yingge Dance" (普宁南山英歌舞).

## 2. Global Memory & Context Understanding

### Gemini 3 Flash
- **Theme Recognition**: Accurately captured the core theme: "普宁南山英歌舞的历史渊源、艺术创新、现代传承挑战及其在全球化背景下的文化传播" (Historical origins, artistic innovation, modern transmission challenges, and cultural spread of Puning Nanshan Yingge Dance).
- **Speaker Diarization**: Successfully identified **3 distinct speakers**:
  - `A`: The Yingge Dance expert/inheritor (Male, Chaoshan accent, authoritative).
  - `B`: The student interviewer from Fudan University (Polite, professional).
  - `C`: Another student member (Clinical medicine/nursing background).
- **Conclusion**: Excellent high-level understanding of the complex interview dynamics.

### Gemini 3.1 Flash Lite
- **Theme Recognition**: Captured a slightly more generic theme: "介绍和讨论“南山英歌”舞蹈团队的起源、发展、核心竞争力及其推广与创新" (Introduction and discussion of the Nanshan Yingge dance team's origins, development, etc.).
- **Speaker Diarization**: Only identified **2 speakers**:
  - `speaker_1`: The interviewer.
  - `speaker_2`: The interviewee/expert.
- **Conclusion**: Missed the nuance of the third speaker (the secondary student) and provided a slightly less detailed contextual summary.

## 3. Transcription Accuracy (Qualitative Sample)

A qualitative review of the first major transcribed chunk (Chunk 1) reveals significant differences in raw transcription accuracy and semantic alignment.

**Gemini 3 Flash (High Accuracy):**
> **B**: 这是您年轻时候照片吗？
> **A**: 这不是最年轻。是九十年代拍的。九四、九五年前后拍的。
> **B**: 等下出来再拍，等下出来。噢，好的。
> ...
> **A**: 这里呢，这里就是南山英歌传承基地。这个基地是2020年1月14号落成的...

**Gemini 3.1 Flash Lite (Lower Accuracy / Hallucinations):**
> **speaker_1**: 那是你年轻时候的照片吗？
> **speaker_2**: 也是那也是年轻。
> **speaker_1**: 哎是90年代拍的？
> **speaker_2**: 90年代那时候还没年轻的。
> **speaker_1**: 把大梳拉把大梳拉。(Severe mishearing of "等下出来再拍")
> ...
> **speaker_2**: 这个球就是难得英歌的水种基地。(Mishearing of "南山英歌传承基地")

### Analysis of Discrepancies:
1. **Verbatim Accuracy**: `gemini-3-flash` demonstrates vastly superior phonetic recognition, especially dealing with the speaker's strong Chaoshan accent and ambient noise. It correctly identifies "传承基地" (Inheritance Base), whereas `flash-lite` hallucinates "水种基地".
2. **Contextual Correction**: `gemini-3-flash` correctly parses the conversational overlap ("等下出来再拍"), while `flash-lite` outputs phonetically similar but semantically nonsensical phrases ("把大梳拉").
3. **Punctuation and Flow**: `gemini-3-flash` formats the output into clean, readable sentences, whereas `flash-lite` struggles with sentence boundaries and generates highly fragmented dialogue.

## 4. Performance & Robustness
- **Payload Handling**: Both models successfully processed the 5-minute chunks (~10MB chunks). Notably, `gemini-3.1-flash-lite` handled the forced `inlineData` transmission (Base64 encoded audio in the JSON payload) without hitting `413 Payload Too Large` limits per chunk, proving the chunking strategy is robust.
- **State Machine Stability**: The LangGraph state machine flawlessly maintained the sliding window context across 12 sequential chunks for both runs.

## 5. Final Verdict
For professional-grade long-audio STT tasks (especially those involving heavy accents, domain-specific terminology, and multi-speaker dynamics), **`gemini-3-flash-preview` is the clear winner**. 

While `gemini-3.1-flash-lite-preview` successfully navigated the API mechanics and workflow, its acoustic recognition capabilities and context-awareness are significantly weaker in this specific real-world scenario, resulting in unacceptable word error rates for professional transcription.