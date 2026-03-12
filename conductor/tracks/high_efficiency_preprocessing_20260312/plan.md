# Implementation Plan: High-Efficiency Large Audio Preprocessing (2h+ Optimization)

## Phase 1: Multi-Threaded Segmentation Infrastructure
- [ ] Task: Create a new utility `app/parallel_processor.py` for managing thread pools and segment tasks.
- [ ] Task: Implement a "Segmenter" that divides a 2h+ audio file into large, overlapping-safe blocks (e.g., 20m) without loading the whole file into RAM.
- [ ] Task: Write unit tests in `tests/test_parallel_processor.py` to verify segment accuracy and thread safety.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure' (Protocol in workflow.md)

## Phase 2: Parallel Preprocessing Logic (VAD, Resampling, Normalization)
- [ ] Task: Refactor `app/vad_processor.py` to support being called in parallel for different segments.
- [ ] Task: Update `app/utils.py` normalization and resampling helpers to be thread-safe and efficient for large blocks.
- [ ] Task: Implement the parallel execution loop that runs VAD, LUFS normalization, and resampling across multiple threads.
- [ ] Task: Write unit tests to verify that parallel VAD results are consistent with sequential processing.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Parallel Logic' (Protocol in workflow.md)

## Phase 3: High-Efficiency Compression & Memory Optimization
- [ ] Task: Optimize the `pydub`/`FFmpeg` export settings for maximum speed and "Overall Optimal" compression (Opus/MP3).
- [ ] Task: Implement a streaming-based exporter that writes processed chunks to disk immediately to minimize peak RAM usage.
- [ ] Task: Add instrumentation to monitor RAM usage during 2h+ processing.
- [ ] Task: Write unit tests to verify compression ratio and file integrity for long-form outputs.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Optimization' (Protocol in workflow.md)

## Phase 4: Integration & Validation on 2h Sample
- [ ] Task: Integrate the new `parallel_preprocess_audio` function into the main `preprocess_audio` entry point (with a toggle for 2h+ files).
- [ ] Task: Update `debug_preprocessing_only.py` to use the new high-efficiency workflow for the 2h sample.
- [ ] Task: Run the **Full Validation** on the 2h sample:
    - [ ] Measure total processing time (TTT).
    - [ ] Verify peak RAM usage.
    - [ ] Check VAD chunk continuity and audio quality.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Validation' (Protocol in workflow.md)
