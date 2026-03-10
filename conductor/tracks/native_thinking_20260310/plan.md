# Implementation Plan: Native Thinking Mode & Prompt Optimization

## Phase 1: API & Client Updates [checkpoint: ba048fc]
- [x] Task: Update `GeminiClient` for native Thinking Mode [0b284fb]
    - [x] **Write Tests**: Create a mock response with `thought: true` in the `parts` array to verify extraction logic.
    - [x] **Implement Feature**: 
        - Add `thinking_level` to `Config`.
        - Update `generate_content` payload to include `thinking_config`.
        - Modify response parsing to separate `thought` parts from `text` parts.
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Updates' (Protocol in workflow.md) [ba048fc]

## Phase 2: Prompt Refactoring
- [~] Task: Refactor `app/transcriber.py` Prompt Template
    - [ ] **Write Tests**: Verify the new prompt generator doesn't contain the "thinking block" instructions.
    - [ ] **Implement Feature**: 
        - Replace CoT commands with a "Guidelines" section (`【转写准则】`).
        - Simplify the task description to focus on strict JSON output.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Prompt Refactoring' (Protocol in workflow.md)

## Phase 3: State & Export Integration
- [ ] Task: Update State and Exporter to handle Thoughts
    - [ ] **Implement Feature**: 
        - Update `STTState` to include a `thought` field per chunk.
        - Update `TranscriptExporter` to save thoughts in the JSON output.
        - (Optional) Add a toggle to include thoughts in Markdown as hidden comments or a dedicated section.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: State & Export' (Protocol in workflow.md)

## Phase 4: Final Validation
- [ ] Task: End-to-End Real Audio Verification
    - [ ] **Implement Feature**: Run `test_real_audio.py` with `gemini-3-flash-preview` and `use-local-proxy`.
    - [ ] **Verification**: Ensure Chunk 1 is complete and all thoughts are logged correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Validation' (Protocol in workflow.md)
## Phase: Review Fixes
- [x] Task: Apply review suggestions 4cb9539
