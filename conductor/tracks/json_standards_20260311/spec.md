# Specification: Align with Official Gemini CLI JSON Standards

## Overview
This track focuses on researching how the official `gemini-cli` (or representative Google AI SDK implementations) handles structured JSON requests and response parsing. The findings will be used to improve the robustness and idiomatic quality of the `gemini-transcribe` project's interaction with the Gemini API.

## Functional Requirements
1. **Research Phase**:
   - Use `githubmcp` to investigate the `gemini-cli` repository (or relevant Google Generative AI samples).
   - Identify standard patterns for:
     - Constructing `generateContent` payloads with `response_mime_type: "application/json"`.
     - Handling multipart requests (audio + text).
     - Parsing and validating structured JSON outputs from the model.
     - Error handling for API-specific JSON errors.
2. **Alignment Phase**:
   - Audit `app/gemini_client.py` and `app/transcriber.py` against these standards.
   - Refactor the request/response logic to match the identified best practices.
   - (Optional) Extract a shared JSON utility module if patterns are repeated.

## Non-Functional Requirements
- **Type Safety**: Use Pydantic or Python type hints for payload and response models.
- **Robustness**: Improved handling of malformed JSON or partial model responses.
- **Maintainability**: Clear separation between API transport and model-specific parsing logic.

## Acceptance Criteria
- A summary of researched "official" patterns is provided.
- `app/gemini_client.py` is updated to use standardized request/response structures.
- `app/transcriber.py` is updated to handle JSON parsing more reliably.
- All existing tests pass, and new tests cover the refined logic.

## Out of Scope
- Changing the VAD logic or the LangGraph orchestration flow.
- Modifying the frontend (if any).
- Switching to an official SDK (the project mandate is pure RESTful API).
