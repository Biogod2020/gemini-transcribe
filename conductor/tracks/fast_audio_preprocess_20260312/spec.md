# Specification: Fast Audio Preprocessing for Long Samples (2h+)

## Overview
This track focuses on optimizing the initial preprocessing phase for long audio files (2 hours or more) to ensure they can be efficiently uploaded and processed by Gemini for global context generation. The primary goal is to minimize resource usage and time, even at the cost of some audio fidelity, as long as speech features remain recognizable for speaker profiling and thematic analysis.

## Functional Requirements
- **Concurrent Download and Preprocess**: Implement a utility that can begin audio preprocessing (resampling, normalization, compression) while the source file is still being downloaded.
- **Audio Optimization for Global Pass**:
    - **Target Format**: Opus (Ogg) at 32-48kbps.
    - **Resampling**: Downsample to 16kHz mono.
    - **Normalization**: LUFS normalization to -16.0 LUFS.
    - **Feature Preservation**: Ensure preprocessing parameters do not compromise speech feature recognition (speaker identity and core vocabulary).
- **Resource Efficiency**: Use non-blocking I/O or subprocesses to handle the 2-hour sample without exhausting local memory.

## Non-Functional Requirements
- **Execution Speed**: The preprocessing should ideally complete shortly after the download finishes.
- **Robustness**: Handle partial downloads or network interruptions gracefully.

## Acceptance Criteria
- [ ] Successfully pre-processes a 2-hour Earnings-22 sample from a URL in under 5 minutes after download completion.
- [ ] Output file size is within the 100MB Gemini upload limit for 2-hour samples.
- [ ] The generated global summary from the preprocessed file correctly identifies all speakers and major themes.

## Out of Scope
- Implementation of the full transcription loop (this track ends at the `fileUri` generation for the global pass).
- Handling non-audio file formats.
