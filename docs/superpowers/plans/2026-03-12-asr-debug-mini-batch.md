# Small-Batch ASR Benchmark Debugging Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Successfully run a mini-benchmark (first 3 chunks) for Flash and Flash Lite to identify the safe concurrency threshold and model routing stability.

---

### Task 1: Throttle the Orchestrator
- [ ] Step 1: Add `chunk_limit` to `BenchmarkOrchestrator.run_variant`.
- [ ] Step 2: Reduce Baseline concurrency in `app/graph.py` to 2.
- [ ] Step 3: Commit.

### Task 2: Targeted Mini-Benchmark
- [ ] Step 1: Update `test_scripts/run_full_matrix.py` to use `chunk_limit=3`.
- [ ] Step 2: Run debugging run for Flash Lite (Official).
- [ ] Step 3: Run debugging run for Gemini 3 Flash (Proxy).
- [ ] Step 4: Analyze results and Commit.
