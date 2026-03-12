# Implementation Plan: Standardized ASR Benchmarking Suite (Earnings-22)

## Phase 1: Dependency & Environment Setup [checkpoint: 48b3669]
- [x] Task: Update `pyproject.toml` with benchmarking dependencies (`datasets`, `evaluate`, `jiwer`, `soundfile`). [dfcdd04]
- [x] Task: Implement `app/utils.py` text normalization helpers. [9134bd3]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Implementation of Benchmarking Script [checkpoint: 867f4a1]
- [x] Task: Create `scripts/benchmark.py` with HF streaming integration. [e4bfc8a]
- [x] Task: Re-implement `scripts/benchmark.py` to invoke the full `STTGraph` workflow. [8e5ed03]
- [x] Task: Implement the model comparison loop (Gemini 3 Flash vs 3.1 Flash Lite). [8e5ed03]
- [x] Task: Add ground-truth alignment and WER calculation logic for long-form audio. [8e5ed03]
- [x] Task: Conductor - User Manual Verification 'Phase 2: Script Implementation' (Protocol in workflow.md)

## Phase 3: Audio Preprocessing & Normalization Utility
- [x] Task: Implement a universal audio loader in `app/utils.py` that supports multiple formats (MP3, M4A, etc.) using `pydub`. [b858ad1]
- [x] Task: Implement **LUFS Normalization (EBU R128)** with a target of **-16.0 LUFS**. [b217b85]
- [ ] Task: Integrate automatic resampling to **16kHz 16-bit Mono** into the preprocessing pipeline.
- [ ] Task: Add **DC Offset removal** and **Silence Padding (100ms)**.
- [ ] Task: Update the `STTGraph` or `ASRBenchmark` to invoke this preprocessing before VAD.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Audio Preprocessing' (Protocol in workflow.md)

## Phase 4: Feasibility Validation (2h Audio)
- [ ] Task: Identify a ~2-hour long audio file from the Earnings-22 `test` split.
- [ ] Task: Run the **complete standardized workflow** (Normalization -> VAD -> Graph) on this 2h file.
- [ ] Task: Verify Global Memory generation and File API performance for the large file.
- [ ] Task: **CRITICAL CHECK**: If the 2h file triggers unrecoverable errors, HALT and await user instructions.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Feasibility' (Protocol in workflow.md)

## Phase 5: Validation & Baseline Run
- [ ] Task: Run the benchmark on 3 random long-form samples from Earnings-22.
- [ ] Task: Generate the official comparative report in `docs/benchmarks/`.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Validation' (Protocol in workflow.md)
