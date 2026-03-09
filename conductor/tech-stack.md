# Tech Stack: High-Precision Long Audio STT Agent (MVP)

## Backend & Core Logic
- **Primary Language**: **Python (managed by uv)** for high-performance audio processing and AI orchestration.
- **Workflow Orchestration**: **LangGraph (Python)** or **FastAPI** to manage the core state machine and sliding window transcription logic.
- **Environment Management**: **uv** for fast, reliable, and deterministic project and environment management.

## AI & Audio Processing
- **AI Model**: `gemini-3.0-flash-preview` accessed via direct HTTP RESTful API (using `httpx` or `requests`) to minimize dependencies.
- **VAD Segmentation**: **Silero VAD** (running on local CPU via `onnxruntime`) for intelligent, high-speed audio splitting.
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
