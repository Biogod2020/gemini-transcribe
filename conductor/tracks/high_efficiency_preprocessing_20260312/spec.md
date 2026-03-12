# Specification: High-Efficiency Large Audio Preprocessing (2h+ Optimization)

## Overview
This track focuses on optimizing the **local preprocessing stage** (VAD, Resampling, Normalization, and Compression) for extremely long audio files (2h+). The goal is to achieve maximum processing speed with minimum resource consumption (RAM/CPU) through multi-threaded segmentation and optimized computation, ensuring the system can handle large samples without performance degradation.

## Functional Requirements
1.  **Multi-Threaded Segmentation**:
    -   Divide the 2h+ source audio into large temporary segments (e.g., 20-30 minute blocks).
    -   Process these segments in parallel threads for VAD detection, normalization (LUFS), and resampling (16kHz).
2.  **Advanced Preprocessing Logic**:
    -   Optimize the **Silero VAD** pass (using ONNX Runtime) to handle long audio efficiently in parallel.
    -   Implement **LUFS Normalization (-16.0 LUFS)** and **DC Offset Removal** across parallel segments.
3.  **High-Efficiency Compression**:
    -   Optimize the final chunk compression (Opus or MP3) to balance speed, file size, and CPU usage (aiming for "Overall Optimal" as requested).
4.  **Memory Management**:
    -   Ensure peak RAM usage remains stable during 2h+ processing by utilizing streaming or segment-based loading instead of full-file buffers.

## Non-Functional Requirements
-   **Maximum Speed**: Significantly reduce processing time (TTT) for 2h files compared to sequential processing (target >2x speedup on multi-core systems).
-   **Minimum Resources**: Maintain a low memory footprint and efficient CPU utilization across multiple threads.
-   **Robustness**: 100% success rate on 2h+ samples (no Out-of-Memory or disk space errors).

## Acceptance Criteria
-   Successfully process a 2h sample using multi-threaded segmentation without errors.
-   VAD output chunks are correctly detected and named, matching or exceeding sequential processing quality.
-   Measurable improvement in processing speed (TTT) for the 2h sample.
-   All preprocessing tasks (resampling, normalization, VAD) are completed within the parallel workflow.

## Out of Scope
-   Gemini API calls, STT transcription, and sliding window orchestration.
-   Global memory generation or final transcript merging.
-   Modifications to the `STTGraph` or `ASRBenchmark` beyond the `preprocess_audio` utility.
