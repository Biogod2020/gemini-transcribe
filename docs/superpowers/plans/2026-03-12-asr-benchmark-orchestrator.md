# ASR Benchmark Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable benchmarking framework to evaluate multiple models and strategies (SOTA vs. Baseline) with parallel execution and 6-dimension scoring.

---

### Task 1: Refactor Graph Nodes for DRY & Concurrency
- [ ] Step 1: Extract `_request_transcription` helper in `app/graph.py`.
- [ ] Step 2: Implement `parallel_transcribe_node` with `asyncio.Semaphore(5)`.
- [ ] Step 3: Update `STTState` and `build_stt_graph` with strategy routing.
- [ ] Step 4: Commit.

### Task 2: Implement Benchmark Orchestrator
- [ ] Step 1: Build `MetricsCalculator` in `app/metrics.py` (WER, MER, WIL, RTF).
- [ ] Step 2: Implement `BenchmarkOrchestrator` core loop.
- [ ] Step 3: Add reporting logic to `output/benchmark_matrix_results.json`.
- [ ] Step 4: Commit.

### Task 3: Execution & Validation
- [ ] Step 1: Create `test_scripts/run_full_matrix.py`.
- [ ] Step 2: Run 4-variant matrix test on 2h sample.
- [ ] Step 3: Verify 6-dimension report completeness.
- [ ] Step 4: Commit.
