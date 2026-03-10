# Specification: Native Thinking Mode & Prompt Strategy Optimization

## Overview
This track implements Gemini's native "Thinking Mode" using the `thinking_level` parameter. It also refactors the transcription prompt to move reasoning logic into a "Guidelines" section, ensuring a clean separation between the model's internal processing and the final structured JSON output.

## Functional Requirements

### 1. Native Thinking Integration
- **thinking_level**: Configure the API to use `thinking_level` (options: `MINIMAL`, `LOW`, `MEDIUM`, `HIGH`). Default will be `MEDIUM`.
- **Thought Extraction**: Update the API response parser to iterate through the `parts` array. 
    - Parts with `thought: true` will be extracted as logs/metadata.
    - Parts without the `thought` flag will be treated as the primary content (JSON).
- **Thinking as Logs**: Print the model's thinking process to the console in real-time during processing.

### 2. Prompt Strategy Refactoring
- **Guidelines vs. Force**: Instead of a "think and then output" command, the prompt will provide a `【转写准则与逻辑指导】` section. 
- **Instructional Focus**: These guidelines will instruct the model on how to handle Teochew accents, reconcile historical context from previous segments, and normalize speaker intent while maintaining verbatim fidelity.
- **Schema Enforcement**: Ensure the model understands that the *final output* must be strictly valid JSON, benefiting from the internal reasoning.

### 3. Data Integrity & Metadata
- **Thought Storage**: Add a `thought` field to each chunk in the `STTState` and the exported `.json` file to preserve the reasoning for audit/debugging.
- **Improved Parsing**: Strengthen the `GeminiClient` to handle cases where the model might still return markdown blocks despite native mode.

## Non-Functional Requirements
- **Robustness**: Gracefully handle models or endpoints that might not support the new `thinking_config`.
- **Latency**: Account for the increased reasoning time by using the 300s timeout.

## Acceptance Criteria
- [ ] API requests include `thinking_config` with `thinking_level: MEDIUM`.
- [ ] Transcription results no longer contain logic fragments (like Chunk 1's previous failure).
- [ ] Model thoughts are visible in logs and saved in the output JSON.
- [ ] `test_run_gemini_3_flash_preview_transcript.md` contains 100% complete and accurate dialogue.