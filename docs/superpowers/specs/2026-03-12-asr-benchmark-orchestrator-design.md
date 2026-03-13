# Specification: ASR Benchmark Orchestrator & Matrix Testing

## 1. Overview
This design defines a unified benchmarking framework for evaluating ASR model performance across different strategies (SOTA vs. Baseline) and models (Flash vs. Flash Lite). It emphasizes concurrency safety, error tolerance, and multi-dimensional performance analysis.

## 2. Architectural Components

### 2.1 LangGraph Extension (`app/graph.py`)
- **Core Abstraction**: Refactor transcription logic into a shared `_request_transcription` helper to keep nodes DRY.
- **SOTA Path**: Sequential processing using `transcribe_chunk_node` with N-2 context.
- **Baseline Path**: New `parallel_transcribe_node` utilizing `asyncio.Semaphore(5)` to strictly enforce concurrency limits.
- **Error Propagation**: Use `asyncio.gather(..., return_exceptions=True)`. Failed chunks will be marked with `[ERROR: <reason>]` in the transcript instead of crashing the run.

### 2.2 Benchmark Orchestrator (`app/benchmark_orchestrator.py`)
- **Matrix Config**: Supports testing various combinations of `(model, strategy, concurrency)`.
- **Environment Isolation**: Automatically resets state and cleans temp files between runs.
- **SOTA Scoring (6-Dimension Matrix)**:
    1. **WER** (Word Error Rate): Core accuracy metric.
    2. **MER** (Match Error Rate): Robustness against alignments.
    3. **WIL** (Word Information Lost): Capturing essential content.
    4. **RTF** (Real-Time Factor): Speed efficiency (Processed Time / Audio Duration).
    5. **Latency**: Time-to-first-chunk and average chunk turnaround.
    6. **Coherence Score**: Qualitative/LLM-based check on speaker consistency.

## 3. Implementation Details
- Use a **Prompt Factory** to switch between context-heavy (SOTA) and pure-transcription (Baseline) instructions.
- Ensure the 100MB Base64 threshold logic is centralized in `app.utils`.

## 4. Acceptance Criteria
- [ ] Successfully executes the full matrix (4+ variants) without manual intervention.
- [ ] Strictly limits parallel API calls to 5 concurrent requests.
- [ ] Gracefully handles partial failures (e.g., 1 chunk fails but 35 succeed).
- [ ] Generates a machine-readable JSON leaderboard and a human-readable Markdown summary.
