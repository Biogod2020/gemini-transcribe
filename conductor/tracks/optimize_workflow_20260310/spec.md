# Specification: Optimize Transcription Workflow

## Overview
This track aims to optimize the core transcription workflow to improve output quality, contextual understanding, and systemic efficiency. The key improvements involve enriching the initial global analysis, transitioning from a sliding window to full-context injection, refining the VAD chunking strategy for longer segments, and implementing Chain-of-Thought (CoT) prompting for logical, comprehension-driven transcription.

## Functional Requirements

### 1. Enriched Global Analysis
- **Detailed Insights:** Enhance the prompt in `app/global_memory_generator.py` to extract richer and more helpful information during the initial "listen-all" pass (e.g., overarching tone, key decisions, complex narrative structures, rather than just basic themes and speakers).

### 2. Full-Context Injection (Replacing Sliding Window)
- **All Previous Transcripts:** Modify `app/transcriber.py` to inject the *entirety* of the previously transcribed text array into the prompt for the current chunk, rather than only the N-2 sliding window.
- **Dynamic Contextual Updates:** By passing the full historical context, allow the model to naturally infer updates to the global state (speakers, themes) without requiring programmatic JSON merges into the core `global_memory` object.

### 3. Optimized Audio Chunking (VAD)
- **Natural Silence Driven with Bounds:** Update `app/vad_processor.py`. The chunking logic must target natural silence points but enforce duration boundaries: chunks must be **no less than 7 minutes** and **no more than 10 minutes** long. This reduces fragmentation and provides longer continuous thoughts to the model.

### 4. SOTA Prompting with Chain-of-Thought (CoT)
- **Comprehension before Transcription:** Update the prompt template in `app/transcriber.py`. Explicitly instruct the model to use a "think step-by-step" or "analyze" block to understand the audio's logic, context, and speaker intent *before* outputting the final JSON transcription.
- **Logical Flow:** Ensure the prompt emphasizes transcribing based on logical comprehension, avoiding rigid, nonsensical word-for-word mapping if the audio is slurred or misspoken, while remaining faithful to the original content.

## Non-Functional Requirements
- **Performance:** Ensure the model `gemini-3.1-flash-lite-preview` can handle the increased token payload of the full-context injection without significant latency degradation or context window overflow.
- **Robust Parsing:** The system must accurately parse the final JSON from the model's response, gracefully ignoring the initial CoT/thinking blocks in the output text.

## Acceptance Criteria
- [ ] Global memory extraction returns a demonstrably richer set of insights.
- [ ] VAD consistently produces chunks strictly between 7 and 10 minutes (unless the final chunk is shorter).
- [ ] The LangGraph state machine passes the complete history of transcripts to every subsequent chunk generation request.
- [ ] The model generates a visible "thinking" or "analysis" text before the final structured JSON in its raw response, demonstrating CoT.
- [ ] The final parsed transcription remains valid JSON despite the CoT text.