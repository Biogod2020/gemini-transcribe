# Implementation Plan: Fast Audio Preprocessing for Long Samples (2h+)

## Phase 1: Dependency & Utility Setup
- [x] Task: Update `pyproject.toml` with `httpx` and `ffmpeg-python` (or similar) for streaming. [d3d8d4c]
- [x] Task: Implement `app/downloader.py` to handle chunked streaming from a URL. [122a7d0]
- [~] Task: Conductor - User Manual Verification 'Phase 1: Setup' (Protocol in workflow.md)

## Phase 2: Concurrent Download & Preprocessing Utility
- [ ] Task: Create `scripts/fast_preprocess.py` to pipe `httpx` stream to **multiple** outputs:
    - **Output 1**: Highly compressed Opus (32kbps) for Global Pass.
    - **Output 2**: High-Quality source (e.g., 128kbps Opus or raw stream) as local reference for chunking.
- [ ] Task: Implement `-16.0 LUFS` normalization and `16kHz 16-bit Mono` resampling in the ffmpeg pipeline for the Global Pass output.
- [ ] Task: Configure Opus encoding at `32kbps` for the Global Pass to ensure the 2-hour file stays under 100MB.
- [ ] Task: Add basic error handling for network interruptions and FFmpeg failures.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Utility' (Protocol in workflow.md)

## Phase 3: Gemini Integration & Validation
- [ ] Task: Update `app/gemini_client.py` to support uploading the preprocessed file for the global pass.
- [ ] Task: Implement a validation script to run the full "Download -> Fast Preprocess -> Gemini Upload -> Global Summary" flow.
- [ ] Task: Benchmark the end-to-end time on a 2-hour Earnings-22 sample.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation' (Protocol in workflow.md)
