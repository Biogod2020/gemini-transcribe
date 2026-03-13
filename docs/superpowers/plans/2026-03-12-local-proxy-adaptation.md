# Local Proxy Adaptation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adapt the system to work seamlessly with the `gcli2api` local proxy on port 7861, forcing inline data mode for reliability.

**Architecture:** `GeminiClient` will automatically lock `use_inline_data` to `True` when a local address is detected. `Config` will be updated to point to the correct proxy port.

**Tech Stack:** Python, httpx, Gemini API (REST)

---

### Task 1: Configuration Update

**Files:**
- Modify: `app/config.py`

- [ ] **Step 1: Update default proxy port and model**
- [ ] **Step 2: Commit**

### Task 2: Client Auto-Adaptation

**Files:**
- Modify: `app/gemini_client.py`

- [ ] **Step 1: Implement auto-inline logic in `__init__`**
- [ ] **Step 2: Commit**

### Task 3: End-to-End Validation (Local Proxy)

**Files:**
- Create: `test_scripts/verify_local_proxy_2h.py`

- [ ] **Step 1: Create validation script**
- [ ] **Step 2: Run 2h benchmark**
- [ ] **Step 3: Calculate WER for comparison**
