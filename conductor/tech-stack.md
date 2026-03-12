# Tech Stack: High-Precision Long Audio STT Agent (MVP)

## Backend & Core Logic
- **Primary Language**: **Python (managed by uv)** for high-performance audio processing and AI orchestration.
- **Workflow Orchestration**: **LangGraph (Python)** or **FastAPI** to manage the core state machine and sliding window transcription logic.
- **Environment Management**: **uv** for fast, reliable, and deterministic project and environment management.
- **Data Modeling**: **Pydantic** for request/response validation and serialization.

## AI & Audio Processing
- **AI Model**: `gemini-3-flash-preview` and `gemini-3.1-flash-lite-preview` accessed via direct HTTP RESTful API.
- **VAD Segmentation**: **Silero VAD** (running on local CPU via `onnxruntime`) for intelligent, high-speed audio splitting.
- **Audio Preprocessing**: **FFmpeg** for high-speed linear standardization (16kHz Mono WAV) and overlapping chunking.
- **Summarization Architecture**: **Map-Reduce Parallel Pipeline** for long audio (2h+), ensuring context continuity and bypassing the 100MB Base64 API limit.
- **Audio Conversion**: **pydub** or **librosa** (backed by FFmpeg) for audio format handling.

## Frontend (Web Application)
- **Framework**: **React (TypeScript)** or **Streamlit/Gradio** (for rapid prototyping). Since we previously discussed a web app, we'll stick with **React (TypeScript)** for the production UI.
- **Styling**: **Vanilla CSS**.

## Database & State Management
- **Primary Database**: **PostgreSQL** or **MongoDB** for persistent storage.
- **Session State**: In-memory state tracking using Python's native structures or **Redis** for persistence.

## Infrastructure & DevOps
- **Deployment**: Containerized using **Docker**.
- **Continuous Integration**: GitHub Actions or similar for automated testing and deployment.
