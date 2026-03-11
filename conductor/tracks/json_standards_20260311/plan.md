# Implementation Plan: Align with Official Gemini CLI JSON Standards

## Phase 1: Research and Audit
- [ ] Task: Research `gemini-cli` via `githubmcp`
    - [ ] Search for official `gemini-cli` or `google-gemini` repositories
    - [ ] Examine `generateContent` JSON payload construction
    - [ ] Analyze JSON response parsing and validation logic
    - [ ] Document found patterns in `docs/research_official_patterns.md`
- [ ] Task: Audit existing code against research findings
    - [ ] Identify discrepancies in `app/gemini_client.py`
    - [ ] Identify discrepancies in `app/transcriber.py`
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Research and Audit' (Protocol in workflow.md)

## Phase 2: Refactor Request Construction
- [ ] Task: Standardize Payload Structures
    - [ ] Define Python data classes or Pydantic models for `generateContent` requests
    - [ ] Update `app/gemini_client.py` to use these models for JSON construction
    - [ ] Write unit tests to verify request body structure
- [ ] Task: Refine Multipart Handling
    - [ ] Align file upload and `fileData` payload logic with official patterns
    - [ ] Verify with tests
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Refactor Request Construction' (Protocol in workflow.md)

## Phase 3: Refactor Response Parsing
- [ ] Task: Implement Robust JSON Parsing
    - [ ] Create a robust parsing utility for `response_mime_type: "application/json"` responses
    - [ ] Update `app/transcriber.py` and `app/global_memory_generator.py` to use this utility
    - [ ] Add error handling for partial or malformed JSON responses
- [ ] Task: Verify Integration
    - [ ] Run full-loop tests (mocked) to ensure end-to-end compatibility
    - [ ] Ensure `global_memory` and `transcript` extraction still works correctly
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Refactor Response Parsing' (Protocol in workflow.md)
