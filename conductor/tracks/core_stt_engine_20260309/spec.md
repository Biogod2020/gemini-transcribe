# Track Specification: Core Long-Audio STT Engine

## Overview
This track focuses on implementing the core high-precision STT engine using a Python-based stack managed by `uv`. The engine will support long audio files by combining local VAD segmentation with global contextual memory and sliding window transcription using `gemini-3.0-flash-preview`.

## Key Objectives
1. **Local Audio Preprocessing**: Implement a robust Voice Activity Detection (VAD) module using **Silero VAD** and `onnxruntime` to split long audio into manageable chunks at silence points.
2. **Global Memory Generation**: Implement an initial "listen-all" pass using the Gemini API to extract core themes, speaker profiles, and a specialized glossary.
3. **Sliding Window Transcription**: Implement the core transcription loop that uses both the **Global Memory** and a **Sliding Window** (N-2 chunks) of local history to ensure verbatim accuracy and consistent speaker identification across chunks.
4. **State Management**: Develop a persistent state machine to track processing progress and ensure resilience.
5. **JSON-First Output**: Ensure all outputs are strictly structured as JSON to facilitate downstream programmatic consumption.

## Technical Design
- **Segmentation**: Target chunk length is 5 minutes. Splits must occur at silences (>700ms) where possible.
- **Gemini Integration**: Use raw `httpx` for direct RESTful API communication with the Gemini API to maintain minimal dependency and full control.
- **Workflow Orchestration**: Utilize **LangGraph (Python)** for stateful, multi-step agentic workflows.
- **Storage**: Initial implementation will use a local JSON file or a lightweight database for state persistence.

## Success Criteria
- [ ] Successfully split a 10-minute audio file into chunks at natural silence points.
- [ ] Generate a global memory JSON containing at least 3 fields (`theme`, `speakers`, `glossary`).
- [ ] Complete a full transcription of a multi-speaker audio file with consistent speaker IDs across chunks.
- [ ] Handle API rate limits (429) gracefully with exponential backoff.
