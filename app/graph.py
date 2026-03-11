import json
import os
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.gemini_client import GeminiClient
from app.transcriber import build_transcription_prompt, parse_transcription_response

class STTState(TypedDict):
    project_id: str
    global_memory: Dict[str, Any]
    processed_chunks: List[Dict[str, Any]] # [{"chunk_index": 0, "transcript": "...", "raw_json": [...], "thought": "..."}]
    chunks_to_process: List[str] # List of file paths
    current_chunk_index: int
    api_key: str
    model_name: str
    use_inline_data: bool

async def transcribe_chunk_node(state: STTState) -> STTState:
    """
    This node processes the current chunk using Gemini.
    It uploads the chunk, builds the prompt with context, and parses the response.
    """
    current_index = state["current_chunk_index"]
    chunks = state["chunks_to_process"]
    
    if current_index >= len(chunks):
        return state

    file_path = chunks[current_index]
    client = GeminiClient(api_key=state["api_key"], model=state["model_name"], use_inline_data=state.get("use_inline_data", False))
    
    print(f"--- Processing Chunk {current_index}/{len(chunks)}: {os.path.basename(file_path)} ---")
    
    # 1. Upload chunk
    with open(file_path, "rb") as f:
        content = f.read()
    
    file_uri, file_name = await client.upload_file(
        content, 
        mime_type="audio/mpeg", 
        display_name=f"chunk_{current_index}"
    )
    
    # 2. Wait for ACTIVE state (if not using inline data)
    is_ready = await client.poll_file_state(file_name)
    if not is_ready:
        print(f"Error: Chunk {current_index} failed to upload.")
        return state

    # 3. Build Prompt
    prompt = build_transcription_prompt(state["global_memory"], state["processed_chunks"])
    
    # 4. Define Response Schema (Force ARRAY of OBJECTS)
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

    # 5. Generate Transcription
    try:
        response = await client.generate_content(
            prompt=prompt,
            mime_type="audio/mpeg",
            file_uri=file_uri,
            audio_content=content,
            response_schema=response_schema
        )
        
        raw_response = response["data"]
        thoughts = response["thought"]
        
        # Check if raw_response is already a list or needs parsing from a string
        if isinstance(raw_response, list):
            transcript_list = raw_response
        elif isinstance(raw_response, dict) and "transcript" in raw_response:
            transcript_list = raw_response["transcript"]
        else:
            # Fallback if it's a string inside a dict
            transcript_list = raw_response

        # Format transcript as a string for context in next rounds
        if isinstance(transcript_list, list) and all(isinstance(i, dict) for i in transcript_list):
            transcript_str = "\n".join([f"{item.get('speaker_id', 'Unknown')}: {item.get('text', '')}" for item in transcript_list])
        elif isinstance(transcript_list, list):
            transcript_str = "\n".join([str(item) for item in transcript_list])
        else:
            transcript_str = str(transcript_list)
            # If it's just a raw string, we might want to wrap it in a pseudo list for the raw_json field
            transcript_list = [{"speaker_id": "Unknown", "text": transcript_str}]
        
        new_chunk = {
            "chunk_index": current_index,
            "transcript": transcript_str,
            "raw_json": transcript_list,
            "thought": thoughts
        }
        
        return {
            **state,
            "processed_chunks": state["processed_chunks"] + [new_chunk],
            "current_chunk_index": current_index + 1
        }
    except Exception as e:
        print(f"Error transcribing chunk {current_index}: {e}")
        return {
            **state,
            "current_chunk_index": current_index + 1
        }

def finalize_node(state: STTState) -> STTState:
    """
    This node runs after all chunks are processed.
    """
    print("--- Transcription Complete ---")
    return state

def should_continue(state: STTState) -> str:
    """
    Determine if we should continue processing chunks or finalize.
    """
    if state["current_chunk_index"] < len(state["chunks_to_process"]):
        return "transcribe_chunk"
    return "finalize"

def build_stt_graph():
    """
    Builds the LangGraph state machine.
    """
    workflow = StateGraph(STTState)
    
    # Add nodes
    workflow.add_node("transcribe_chunk", transcribe_chunk_node)
    workflow.add_node("finalize", finalize_node)
    
    # Define edges
    workflow.set_entry_point("transcribe_chunk")
    workflow.add_conditional_edges("transcribe_chunk", should_continue, {
        "transcribe_chunk": "transcribe_chunk",
        "finalize": "finalize"
    })
    workflow.add_edge("finalize", END)
    
    return workflow.compile()
