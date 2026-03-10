# Implementation Plan: Optimize Transcription Workflow

## Phase 1: Optimized Audio Chunking (VAD)
- [x] Task: Update VAD logic to enforce 7-10 minute chunk boundaries [71b167e]
    - [x] **Write Tests**: Create or update tests in `tests/test_vad.py` to verify chunks are generated between 7 and 10 minutes based on natural silence points.
    - [x] **Implement Feature**: Modify `get_chunks` in `app/vad_processor.py` to adjust `target_chunk_duration_sec` and ensure the slicing logic strictly adheres to the new minimum (420s) and maximum (600s) constraints.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Optimized Audio Chunking (VAD)' (Protocol in workflow.md)

## Phase 2: Enriched Global Analysis
- [ ] Task: Enhance Global Memory Prompt
    - [ ] **Write Tests**: Update tests in `tests/test_global_memory.py` to verify the extraction of the richer data structure (e.g., tone, decisions, narrative structure).
    - [ ] **Implement Feature**: Update the `self.prompt` string in `app/global_memory_generator.py` to ask for a deeper, more comprehensive analysis of the full audio.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Enriched Global Analysis' (Protocol in workflow.md)

## Phase 3: Full-Context Injection and SOTA Prompting
- [ ] Task: Implement Full-Context Injection
    - [ ] **Write Tests**: Update tests in `tests/test_transcriber.py` to verify that the `build_transcription_prompt` function utilizes the entire `processed_chunks` array instead of just the last two.
    - [ ] **Implement Feature**: Modify `app/transcriber.py` to remove the sliding window slicing (`context_chunks = processed_chunks[-2:]`) and map the entire history into the prompt text.
- [ ] Task: Implement Chain-of-Thought (CoT) Prompting
    - [ ] **Write Tests**: Update tests in `tests/test_transcriber.py` to ensure `parse_transcription_response` can successfully extract the JSON array even if it is preceded by an unstructured "thinking" block.
    - [ ] **Implement Feature**: Update the prompt in `app/transcriber.py` to instruct the model to "think step-by-step", analyze the context logically, and output its reasoning before the final JSON block.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Full-Context Injection and SOTA Prompting' (Protocol in workflow.md)

## Phase 4: End-to-End Validation
- [ ] Task: Verify End-to-End Execution
    - [ ] **Write Tests**: Add any necessary integration assertions to ensure the LangGraph state transitions handle the new prompt structure and chunking correctly.
    - [ ] **Implement Feature**: Run `test_real_audio.py` against a test audio file to confirm the full pipeline (larger chunks -> enriched memory -> full context + CoT generation -> robust parsing) works without errors.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: End-to-End Validation' (Protocol in workflow.md)