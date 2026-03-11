# Implementation Plan: Large Audio Processing and Model Comparison

## Phase 1: Audio Merging Utility [checkpoint: 01507db]
- [x] Task: Implement Audio Merging Script [7a3f854]
    - [x] Create `scripts/merge_audio.py` to sort and merge segments using FFmpeg.
    - [x] Write unit tests in `tests/test_merger.py` to verify sorting and merging logic.
    - [x] Verify that the merged file `data/merged_full_audio.m4a` is correctly generated.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Audio Merging Utility' (Protocol in workflow.md)

## Phase 2: Execution - Gemini 3 Flash (Local)
- [ ] Task: Run STT Workflow with Gemini 3 Flash
    - [ ] Configure `GeminiClient` for local proxy (`http://localhost:8888/v1beta`, key: `123456`).
    - [ ] Process `data/merged_full_audio.m4a` using `gemini-3-flash-preview`.
    - [ ] Export results to `output/gemini_3_flash/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Execution - Gemini 3 Flash (Local)' (Protocol in workflow.md)

## Phase 3: Execution - Gemini 3.1 Flash Lite (Official)
- [ ] Task: Run STT Workflow with Gemini 3.1 Flash Lite
    - [ ] Configure `GeminiClient` for official Google API.
    - [ ] Process `data/merged_full_audio.m4a` using `gemini-3.1-flash-lite-preview`.
    - [ ] Export results to `output/gemini_3_1_lite/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Execution - Gemini 3.1 Flash Lite (Official)' (Protocol in workflow.md)

## Phase 4: Comparison and Reporting
- [ ] Task: Qualitative Analysis
    - [ ] Compare `output/gemini_3_flash/` and `output/gemini_3_1_lite/` transcripts.
    - [ ] Identify discrepancies in technical terms, speaker consistency, and sentence structure.
- [ ] Task: Generate Comparison Report
    - [ ] Create `docs/comparison_report_large_audio.md` with detailed narrative findings.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Comparison and Reporting' (Protocol in workflow.md)
