# Specification: Standardized ASR Benchmarking Suite

## Overview
This track implements a reusable, professional-grade benchmarking suite for the `gemini-transcribe` project. The tool will provide objective performance metrics (Word Error Rate - WER) by streaming standardized datasets from Hugging Face. This modular utility is intended for long-term use to evaluate future model updates and system optimizations.

## Functional Requirements
1. **ASR Benchmarking Module (`scripts/benchmark.py`)**:
   - **Data Source**: Stream `LibriSpeech` (`test-clean`) using `datasets` library.
   - **Streaming Mode**: Fetch data sample-by-sample without full dataset download.
   - **Multi-Model Support**: Simultaneously evaluate both `gemini-3-flash-preview` (local) and `gemini-3.1-flash-lite-preview` (official).
   - **Output Format**: Final results saved to `output/benchmarks/benchmark_YYYYMMDD_HHMMSS.json`.
2. **Core Evaluation Engine**:
   - Integrate `evaluate` and `jiwer` for industry-standard WER calculation.
   - Handle text normalization (case normalization, punctuation removal) to ensure fair comparison.
3. **Engineering Improvements**:
   - Refactor `GeminiClient` interaction to handle fast, small-packet (`inlineData`) requests efficiently.
   - Implement structured logging for the benchmark process.

## Acceptance Criteria
- Dependencies are successfully updated via `uv`.
- The `scripts/benchmark.py` script executes without errors.
- The script processes the requested samples from `LibriSpeech`.
- A final WER score is printed for both models.
