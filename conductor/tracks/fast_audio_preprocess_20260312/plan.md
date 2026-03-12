# Implementation Plan: Fast Audio Preprocessing & Map-Reduce Summary (2h+)

## Phase 1: Fast Standardization & Threshold Detection [checkpoint: 705718]
- [x] Task: Update `pyproject.toml` with `httpx` and `ffmpeg-python`. [d3d8d4c]
- [x] Task: Implement `app/downloader.py` for chunked download. [122a7d0]
- [x] Task: Create `scripts/fast_standardize.py` to convert audio to 16kHz Mono WAV (PCM). [705718]
- [x] Task: Implement logic to calculate projected Base64 size (`file_size * 1.33`) and determine if chunking is needed (>100MB). [705718]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Standardization' (Protocol in workflow.md)

## Phase 2: Overlapping Chunking Utility [checkpoint: 707326]
- [x] Task: Implement `app/utils.py` function `get_overlapping_chunks` using FFmpeg `segment` or `trim`. [707326]
- [x] Task: Configure default segments (e.g., 20m) and overlap (e.g., 2m). [707326]
- [x] Task: Add unit tests to verify overlap integrity at segment boundaries. [707326]
- [x] Task: Conductor - User Manual Verification 'Phase 2: Chunking' (Protocol in workflow.md)

## Phase 3: Parallel Map-Reduce Integration [checkpoint: 1708704]
- [x] Task: Update `app/global_memory_generator.py` to support `Map` phase (Parallel summary of all chunks). [1708704]
- [x] Task: Implement `Reduce` phase prompt to synthesize multiple segment summaries into one 6-dimension Global Summary. [1708704]
- [x] Task: Implement concurrency control (e.g., `asyncio.gather`) for parallel Gemini API calls. [1708704]
- [x] Task: Final full-flow validation on the 2-hour Earnings-22 sample. [1708704]
- [x] Task: Conductor - User Manual Verification 'Phase 3: Map-Reduce' (Protocol in workflow.md)
