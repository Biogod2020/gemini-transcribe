# Implementation Plan: Standardized ASR Benchmarking Suite (Earnings-22)

## Phase 1: Dependency & Environment Setup [checkpoint: 48b3669]
- [x] Task: Update `pyproject.toml` with benchmarking dependencies (`datasets`, `evaluate`, `jiwer`, `soundfile`). [dfcdd04]
- [x] Task: Implement `app/utils.py` text normalization helpers. [9134bd3]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Implementation of Benchmarking Script [checkpoint: b930ae9]
- [x] Task: Create `scripts/benchmark.py` with HF streaming integration. [e4bfc8a]
- [x] Task: Re-implement `scripts/benchmark.py` to invoke the full `STTGraph` workflow. [8e5ed03]
- [x] Task: Implement the model comparison loop (Gemini 3 Flash vs 3.1 Flash Lite). [8e5ed03]
- [x] Task: Add ground-truth alignment and WER calculation logic for long-form audio. [8e5ed03]
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Script Implementation' (Protocol in workflow.md)

## Phase 3: Audio Normalization Utility
- [ ] Task: Implement audio normalization in `app/utils.py` or `scripts/benchmark.py`.
- [ ] Task: Use `pydub` or `FFmpeg` to standardize volume (Peak Normalization).
- [ ] Task: Ensure all benchmark samples are converted to 16kHz Mono.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Audio Normalization' (Protocol in workflow.md)

## Phase 4: Validation & Baseline Run
- [ ] Task: Run the benchmark on 3 random long-form samples from Earnings-22.
- [ ] Task: Generate the official comparative report in `docs/benchmarks/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Validation' (Protocol in workflow.md)
