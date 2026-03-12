# Specification: Fast Audio Preprocessing & Adaptive Summarization

## Overview
This track focuses on maximizing the processing speed and semantic coherence for long audio files (2h+). The goal is to achieve Single-Pass (one-shot) summarization whenever possible by using ultra-fast, lightweight compression (MP3 32kbps) and adaptive pass-through logic, defaulting to Map-Reduce only for extremely long sessions.

## Functional Requirements
- **Adaptive Standardization Pass**:
    - **Smart Pass-through**: If the source is already compressed (MP3/M4A) and projected Base64 size < 95MB, use the original file without transcoding.
    - **Fast MP3 Compression**: If transcoding is needed (e.g., source is WAV or too large), convert to 16kHz Mono MP3 at 32kbps using `libmp3lame` (much faster than Opus).
- **Projected Base64 Calculation**: Automatically calculate the final Base64 size (`final_file_size * 1.33`) to verify it stays under the 100MB API limit.
- **Adaptive Map-Reduce (Fallback)**:
    - Only trigger if the Fast MP3 version still exceeds 75MB (approx. >5 hours of audio).
    - Use 45-minute chunks with 5-minute overlap for maximum context retention.
- **Resource Efficiency**: Prioritize Single-Pass summary to maintain better narrative coherence than Map-Reduce.

## Acceptance Criteria
- [ ] Successfully processes a 2-hour audio file in under 30 seconds.
- [ ] Correctly identifies when to skip transcoding (Pass-through).
- [ ] Produces a standardized file that is consistently < 100MB Base64 for audio up to 4 hours.
- [ ] Successfully generates a Global Summary using the Single-Pass approach for the 2-hour sample.
