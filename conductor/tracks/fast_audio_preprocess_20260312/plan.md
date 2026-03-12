# Implementation Plan: Adaptive Fast Preprocessing & Summary

## Phase 1: Adaptive Standardization Utility [checkpoint: 1717386]
- [x] Task: Update `pyproject.toml` with `httpx` and `ffmpeg-python`. [d3d8d4c]
- [x] Task: Implement `app/downloader.py` for chunked download. [122a7d0]
- [x] Task: Update `scripts/fast_standardize.py` with adaptive logic: [1717386]
    - If source is MP3/M4A and <75MB, use **Pass-through (copy)**.
    - Otherwise, use **Fast MP3 (32kbps libmp3lame)**.
- [x] Task: Implement Base64 size verification and Single-Pass vs Map-Reduce decision tree. [1717386]
- [x] Task: Conductor - User Manual Verification 'Phase 1: Adaptive Logic' (Protocol in workflow.md)

## Phase 2: Refined Single-Pass Validation (2h Sample) [checkpoint: 1718253]
- [x] Task: Run the adaptive script on the 2-hour Earnings-22 sample. [1718253]
- [x] Task: Verify the resulting file size and audio quality. [1718253]
- [x] Task: Trigger `GlobalMemoryGenerator` using the Single-Pass SOTA prompt. [1718253]
- [x] Task: Conductor - User Manual Verification 'Phase 2: Validation' (Protocol in workflow.md)

## Phase 3: Fallback Map-Reduce (if needed) [checkpoint: 1708704]
- [x] Task: Implement overlapping chunking logic in `app/utils.py`. [707326]
- [x] Task: Update `app/global_memory_generator.py` for Map-Reduce. [1708704]
- [x] Task: Update chunking parameters to 45m chunks / 5m overlap for better coherence in fallback scenarios. [1708704]
- [x] Task: Conductor - User Manual Verification 'Phase 3: Fallback' (Protocol in workflow.md)
