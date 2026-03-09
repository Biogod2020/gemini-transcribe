from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

class STTState(TypedDict):
    project_id: str
    global_memory: Dict[str, Any]
    processed_chunks: List[Dict[str, Any]] # [{"chunk_index": 0, "transcript": "..."}]
    chunks_to_process: List[str] # List of file paths
    current_chunk_index: int

def transcribe_chunk_node(state: STTState) -> STTState:
    """
    This node processes the current chunk using Gemini.
    (Mocked implementation for graph structure testing)
    """
    # Real implementation will extract N-2 context and call GeminiClient
    current_index = state["current_chunk_index"]
    
    if current_index < len(state["chunks_to_process"]):
        # Mock transcription result
        new_chunk = {
            "chunk_index": current_index,
            "transcript": f"Mock transcript for chunk {current_index}"
        }
        
        return {
            **state,
            "processed_chunks": state["processed_chunks"] + [new_chunk],
            "current_chunk_index": current_index + 1
        }
    return state

def finalize_node(state: STTState) -> STTState:
    """
    This node runs after all chunks are processed.
    """
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
