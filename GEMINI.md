# Gemini Transcribe

A professional-grade long-audio speech-to-text (STT) engine leveraging Google Gemini and LangGraph for high-fidelity transcription with global context awareness and speaker consistency.

## Project Overview
This project addresses the challenges of transcribing very long audio files (e.g., meetings, lectures) by:
1.  **VAD Segmentation**: Using Silero VAD to intelligently split audio into chunks at natural silence points (>700ms).
2.  **Global Context Generation**: An initial "listen-all" pass to extract themes, speaker profiles, and technical glossaries.
3.  **Sliding Window Transcription**: Orchestrating a LangGraph-based loop that injects $N-2$ (previous two chunks) context into each transcription request to ensure semantic continuity and speaker alignment.
4.  **Resumable Uploads**: Implementing the Google File API's resumable upload protocol for robust handling of large audio segments.

## Tech Stack
-   **Language**: Python >= 3.12
-   **Orchestration**: LangGraph (for the transcription state machine)
-   **Audio Processing**: Silero VAD, Pydub, ONNX Runtime
-   **API Integration**: HTTPX (for direct RESTful interaction with Gemini API)
-   **Dependency Management**: `uv`

## Building and Running

### Prerequisites
-   `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
-   FFmpeg installed (for audio export)
-   A Gemini API key (placed in `.env/geminiapikey.txt`)

### Setup
```bash
# Sync dependencies
uv sync
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run VAD tests specifically
uv run pytest tests/test_vad.py
```

### Executing Transcription
Currently, the core logic is accessible via `main.py` and the `app/` modules. 
TODO: Add a CLI entry point for processing local audio files.

## Development Conventions

### Code Style
-   Follow standard PEP 8 conventions.
-   Use type hints for all function signatures.
-   Asynchronous programming is preferred for I/O-bound tasks (API calls, file polling).

### Testing
-   **Unit Tests**: Located in `tests/`, covering VAD logic, Gemini client mocking, and Graph transitions.
-   **Mocking**: Use `respx` for mocking HTTP calls to the Gemini API in tests.
-   **Validation**: Every major phase includes a Conductor checkpoint for manual verification.

### Architecture
-   `app/vad_processor.py`: Handles Silero VAD initialization and segment detection.
-   `app/gemini_client.py`: Manages file uploads, polling, and content generation.
-   `app/graph.py`: Defines the LangGraph state machine (`STTState`) and node logic.
-   `app/transcriber.py`: Contains prompt engineering and response parsing logic.
