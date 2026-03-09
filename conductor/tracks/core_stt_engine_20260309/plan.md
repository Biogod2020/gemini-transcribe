# Implementation Plan: Core Long-Audio STT Engine

## Phase 1: Environment Setup and Initial Dependencies [checkpoint: 89c10c2]
- [x] Task: Initialize UV environment and install core Python dependencies (9d5e8ea)
    - [x] `uv add langgraph httpx onnxruntime silero-vad pydub pytest pytest-asyncio`
    - [x] Configure `pyproject.toml` for standard project layout.
- [x] Task: Set up local project structure (app, tests, data) (9d5e8ea)
    - [x] Create `app/`, `tests/`, and `data/` directories.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment Setup' (Protocol in workflow.md) (89c10c2)

## Phase 2: Local VAD Segmentation Module [checkpoint: 159fd3e]
- [x] Task: Implement Silence-Based Segmentation using Silero VAD (4c4e2f8)
    - [x] **Write Tests**: Create `tests/test_vad.py` to verify silence detection and chunking.
    - [x] **Implement Feature**: Develop `app/vad_processor.py` to split audio at natural silence points (>700ms).
- [x] Task: Implement Audio Export to MP3/WAV Chunks (4de6964)
    - [x] **Write Tests**: Verify file outputs for named chunks.
    - [x] **Implement Feature**: Use `pydub` or similar to export chunk segments.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Local VAD Segmentation' (Protocol in workflow.md) (159fd3e)

## Phase 3: Global Context Generator [checkpoint: 7b5a663]
- [x] Task: Implement Gemini File Upload and Polling Logic (29da2c8)
    - [x] **Write Tests**: Mock Gemini API to verify file upload and state polling.
    - [x] **Implement Feature**: Develop `app/gemini_client.py` for direct RESTful interaction with Google File API.
- [x] Task: Implement Global Memory Generation Pass (2e141e6)
    - [x] **Write Tests**: Verify JSON extraction of theme, speakers, and glossary.
    - [x] **Implement Feature**: Create prompt logic for the initial "listen-all" pass.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Global Context' (Protocol in workflow.md) (7b5a663)

## Phase 4: Core Transcription Loop (LangGraph)
- [~] Task: Define STT State Machine with LangGraph
    - [ ] **Write Tests**: Verify graph transitions and state persistence.
    - [ ] **Implement Feature**: Develop `app/graph.py` to orchestrate the sliding window transcription loop.
- [ ] Task: Implement Sliding Window Transcription with Local Context
    - [ ] **Write Tests**: Verify N-2 chunk context injection.
    - [ ] **Implement Feature**: Implement the final transcription prompt and response parsing logic.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Core Loop' (Protocol in workflow.md)

## Phase 5: Data Assembly and Export
- [ ] Task: Implement Final Transcript Aggregation
    - [ ] **Write Tests**: Verify seamless stitching of JSON chunks into a final document.
    - [ ] **Implement Feature**: Create aggregation logic and final output formatting.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Export' (Protocol in workflow.md)
