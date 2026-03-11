# Specification: Large Audio Processing and Model Comparison

## Overview
This track aims to test the `gemini-transcribe` workflow's capability to handle large audio files. It involves merging four chronological audio segments into a single file and comparing the transcription performance of `gemini-3-flash-preview` (via local proxy) and `gemini-3.1-flash-lite-preview` (via official API).

## Functional Requirements
1.  **Audio Merging**:
    -   Identify files in the `data/` directory.
    -   Sort files chronologically based on the naming pattern `2026年01月26日 下午XX点YY分.m4a`.
    -   Merge the segments into a single `merged_full_audio.m4a` using FFmpeg.
2.  **Dual-Model Processing**:
    -   Process the merged file using the full STT workflow (VAD -> Global Memory -> Sliding Window Transcription).
    -   **Run 1**: Use `gemini-3-flash-preview` via the local proxy (`http://localhost:8888/v1beta`).
    -   **Run 2**: Use `gemini-3.1-flash-lite-preview` via the official Google API.
3.  **Result Comparison**:
    -   Analyze the output transcripts from both runs.
    -   Focus on verbatim accuracy, speaker identification consistency, and adherence to the global glossary.
    -   Generate a detailed narrative report highlighting discrepancies and strengths of each model.

## Non-Functional Requirements
-   **Performance**: Merging should be performed without re-encoding to minimize data loss and processing time.
-   **Robustness**: The workflow must handle the increased file size without memory exhaustion or API timeout issues (utilizing the existing resumable upload and sliding window logic).

## Acceptance Criteria
-   A single merged audio file is successfully created.
-   Two complete sets of transcription results (JSON and Markdown) are generated.
-   A `detailed_comparison_report.md` is produced, providing a narrative analysis of the two models' performances.

## Out of Scope
-   Optimizing FFmpeg parameters for compression.
-   Automated Word Error Rate (WER) calculation using ground truth (manual qualitative comparison only).
