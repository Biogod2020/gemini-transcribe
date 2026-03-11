# Implementation Plan: Align with Official Gemini CLI JSON Standards

## Phase 1: Research and Audit [checkpoint: 9838de4]
- [x] Task: Research `gemini-cli` via `githubmcp` [547fbf7]
    - [x] Search for official `gemini-cli` or `google-gemini` repositories
    - [x] Examine `generateContent` JSON payload construction
    - [x] Analyze JSON response parsing and validation logic
    - [x] Document found patterns in `docs/research_official_patterns.md`
- [x] Task: Audit existing code against research findings
    - [x] Identify discrepancies in `app/gemini_client.py`
    - [x] Identify discrepancies in `app/transcriber.py`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Research and Audit' (Protocol in workflow.md)

## Phase 2: Refactor Request Construction [checkpoint: 0c10ba4]
- [x] Task: Standardize Payload Structures
    - [x] Define Python data classes or Pydantic models for `generateContent` requests
    - [x] Update `app/gemini_client.py` to use these models for JSON construction
    - [x] Write unit tests to verify request body structure
- [x] Task: Refine Multipart Handling
    - [x] Align file upload and `fileData` payload logic with official patterns
    - [x] Verify with tests
- [x] Task: Conductor - User Manual Verification 'Phase 2: Refactor Request Construction' (Protocol in workflow.md)

## Phase 3: Refactor Response Parsing [checkpoint: c31c68c]
- [x] Task: Implement Robust JSON Parsing
    - [x] Create a robust parsing utility for `response_mime_type: "application/json"` responses
    - [x] Update `app/transcriber.py` and `app/global_memory_generator.py` to use this utility
    - [x] Add error handling for partial or malformed JSON responses
- [x] Task: Verify Integration
    - [x] Run full-loop tests (mocked) to ensure end-to-end compatibility
    - [x] Ensure `global_memory` and `transcript` extraction still works correctly
- [x] Task: Conductor - User Manual Verification 'Phase 3: Refactor Response Parsing' (Protocol in workflow.md)
