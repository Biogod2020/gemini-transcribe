# Implementation Plan: Standardized ASR Benchmarking Suite

## Phase 1: Dependency & Environment Setup [checkpoint: 48b3669]
- [x] Task: Update `pyproject.toml` with benchmarking dependencies (`datasets`, `evaluate`, `jiwer`, `soundfile`). [dfcdd04]
- [x] Task: Implement `app/utils.py` text normalization helpers. [9134bd3]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Implementation of Benchmarking Script
- [ ] Task: Create `scripts/benchmark.py` with HF streaming integration.
- [ ] Task: Implement the core loop for sending audio to `GeminiClient` and computing WER.
- [ ] Task: Add result persistence (saving to `output/benchmarks/`).
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Script Implementation' (Protocol in workflow.md)

## Phase 3: Validation & Baseline Run
- [ ] Task: Run a benchmark on the first 100 samples of LibriSpeech.
- [ ] Task: Generate the first official baseline report in `docs/benchmarks/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation' (Protocol in workflow.md)
