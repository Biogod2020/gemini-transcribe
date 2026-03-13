import json
import os
import asyncio
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, END
from app.gemini_client import GeminiClient
from app.transcriber import build_transcription_prompt

class STTState(TypedDict):
    project_id: str
    global_memory: Dict[str, Any]
    processed_chunks: List[Dict[str, Any]]
    chunks_to_process: List[str]
    current_chunk_index: int
    api_key: str
    model_name: str
    base_url: str
    use_inline_data: bool
    context_window_size: int
    strategy: Literal["sota", "baseline"]

async def _request_transcription(
    client: GeminiClient, 
    file_path: str, 
    idx: int, 
    prompt: str
) -> Dict[str, Any]:
    """Shared core: Now uses file path to save memory."""
    # 1. Upload (Pass path directly)
    file_uri, file_name = await client.upload_file(file_path, mime_type="audio/mpeg", display_name=f"chunk_{idx}")
    if not await client.poll_file_state(file_name):
        raise RuntimeError(f"Chunk {idx} upload failed.")
        
    # Only read for audio_content if using inline mode
    audio_content = None
    if client.use_inline_data:
        with open(file_path, "rb") as f: audio_content = f.read()

    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "speaker_id": {"type": "STRING"},
                "text": {"type": "STRING"}
            },
            "required": ["speaker_id", "text"]
        }
    }
    
    response = await client.generate_content(
        prompt=prompt, mime_type="audio/mpeg", file_uri=file_uri, 
        audio_content=audio_content, response_schema=response_schema
    )
    
    raw_response = response["data"]
    transcript_list = raw_response if isinstance(raw_response, list) else [{"speaker_id": "Unknown", "text": str(raw_response)}]
    transcript_str = "\n".join([f"{item.get('speaker_id', 'Unknown')}: {item.get('text', '')}" for item in transcript_list])
    
    return {
        "chunk_index": idx, "transcript": transcript_str, 
        "raw_json": transcript_list, "thought": response.get("thought", "")
    }

async def transcribe_chunk_node(state: STTState) -> STTState:
    """Sequential SOTA node with memory optimization."""
    idx = state["current_chunk_index"]
    if idx >= len(state["chunks_to_process"]): return state
    
    client = GeminiClient(api_key=state["api_key"], model=state["model_name"], base_url=state.get("base_url"), use_inline_data=state.get("use_inline_data", False))
    prompt = build_transcription_prompt(state["global_memory"], state["processed_chunks"], context_window_size=state.get("context_window_size", 2))
    
    try:
        new_chunk = await _request_transcription(client, state["chunks_to_process"][idx], idx, prompt)
        return {**state, "processed_chunks": state["processed_chunks"] + [new_chunk], "current_chunk_index": idx + 1}
    except Exception as e:
        print(f"Error in SOTA node: {e}")
        error_chunk = {"chunk_index": idx, "transcript": f"[TRANSCRIPTION_FAILED: {e}]", "raw_json": [], "thought": ""}
        return {**state, "processed_chunks": state["processed_chunks"] + [error_chunk], "current_chunk_index": idx + 1}

async def parallel_transcribe_node(state: STTState) -> STTState:
    """Parallel Baseline node with strict error reporting and 2-concurrency."""
    client = GeminiClient(api_key=state["api_key"], model=state["model_name"], base_url=state.get("base_url"), use_inline_data=state.get("use_inline_data", False))
    semaphore = asyncio.Semaphore(2) # Safe default for debugging
    
    async def sem_request(path, i):
        async with semaphore:
            try:
                prompt = "Please transcribe this audio accurately. Output a JSON array of objects with speaker_id and text."
                return await _request_transcription(client, path, i, prompt)
            except Exception as e:
                print(f"Parallel chunk {i} failed: {e}")
                return {"chunk_index": i, "transcript": f"[TRANSCRIPTION_FAILED: {e}]", "raw_json": [], "thought": ""}

    tasks = [sem_request(p, i) for i, p in enumerate(state["chunks_to_process"])]
    results = await asyncio.gather(*tasks) # No return_exceptions=True, we handle inside
    
    return {**state, "processed_chunks": sorted(results, key=lambda x: x["chunk_index"]), "current_chunk_index": len(state["chunks_to_process"])}

def build_stt_graph():
    workflow = StateGraph(STTState)
    workflow.add_node("sota_transcribe", transcribe_chunk_node)
    workflow.add_node("baseline_transcribe", parallel_transcribe_node)
    
    workflow.set_conditional_entry_point(
        lambda s: s.get("strategy", "sota"),
        {"sota": "sota_transcribe", "baseline": "baseline_transcribe"}
    )
    
    workflow.add_conditional_edges(
        "sota_transcribe",
        lambda s: "continue" if s["current_chunk_index"] < len(s["chunks_to_process"]) else "end",
        {"continue": "sota_transcribe", "end": END}
    )
    workflow.add_edge("baseline_transcribe", END)
    return workflow.compile()
