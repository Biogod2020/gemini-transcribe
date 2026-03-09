# Product Guidelines: High-Precision Long Audio STT Agent (MVP)

## Prose Style & Voice
- **Tone**: Friendly & Accessible. The agent should communicate in a way that is easy for anyone to understand, avoiding overly dense jargon where possible while still maintaining precision.
- **Clarity**: Instructions and feedback should be direct and clear.
- **Consistency**: Use consistent terminology throughout the application and documentation.

## Branding & Identity
- **Core Value**: Premium & Reliable. The focus is on delivering high-quality, trustworthy transcriptions that users can rely on for critical tasks.
- **Visuals & Copy**: The interface and messaging should reflect a sense of professional excellence and stability.

## User Experience (UX) Principles
- **Transparency of Process**: Users should always know what the agent is doing. Provide clear indicators for VAD segmentation, global memory generation, and sliding window transcription progress.
- **Low-Friction Automation**: Once the user uploads the audio, the agent should handle the heavy lifting with minimal further intervention, leading to a "set it and forget it" experience for the majority of the process.
- **Responsive Feedback**: Ensure the interface provides immediate feedback on user actions (e.g., upload confirmation).

## Error Handling & Reliability
- **Transparent & Technical**: When errors occur (e.g., API rate limits, network issues), the agent should provide detailed, technical information to help the user (or a developer) understand exactly what went wrong.
- **Robustness**: Implement exponential backoff for transient errors (like HTTP 429) to ensure the transcription process is resilient.
- **State Persistence**: The core state machine should be resilient to interruptions, allowing for recovery or clear reporting of failure points.
