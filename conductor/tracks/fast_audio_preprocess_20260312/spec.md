# Specification: Fast Audio Preprocessing & Map-Reduce Summary (2h+)

## Overview
This track focuses on maximizing the processing speed for long audio files (2h+) by shifting from a single compressed upload to a parallelized Map-Reduce summarization architecture. This ensures high-fidelity summaries while staying within the 100MB Base64 API limit through intelligent, overlapping chunking.

## Functional Requirements
- **Fast Audio Standardization**: Quickly convert long audio (2h+) to a standard format (16kHz Mono WAV) using linear transcoding (fastest pass).
- **Base64-Aware Chunking Strategy**: 
    - Automatically calculate the projected Base64 size of the standardized file.
    - If `projected_base64_size > 100MB` (approx. >75MB raw WAV file), trigger **Overlapping Chunking**.
- **Overlapping Chunking**: Split the audio into large segments (e.g., 20 minutes) with a 2-minute overlap to ensure no context is lost at boundaries.
- **Parallel Map-Reduce Summary**:
    - **Map Phase**: Concurrently upload chunks and generate individual summaries for each segment using Gemini.
    - **Reduce Phase**: Synthesize all segment summaries into a single cohesive Global Summary following the standard 6-dimension schema.
- **Resource Efficiency**: Maximize CPU utilization through parallel API processing and avoid slow lossy re-encoding (like Opus/MP3) for the summary pass.

## Non-Functional Requirements
- **Execution Speed**: Standardization and chunking should be near-linear with disk I/O (e.g., <60s for 2h audio).
- **Scalability**: Capable of handling 4h+ audio by increasing the number of parallel chunks.

## Acceptance Criteria
- [ ] Successfully standardizes a 2-hour audio file in under 60 seconds.
- [ ] Correctly triggers chunking based on the 100MB Base64 threshold.
- [ ] Concurrently generates segment summaries.
- [ ] Produces a final aggregated Global Summary that synthesizes information accurately across all segments.

## Out of Scope
- Full transcription loop (handled by subsequent STT tracks).
- Real-time streaming output (this focus is on batch preprocessing).
