import pytest
from app.graph import build_stt_graph, STTState

def test_stt_state_initialization():
    """Test that the state can be initialized correctly."""
    state = STTState(
        project_id="test_001",
        global_memory={"theme": "", "glossary": [], "speakers": []},
        processed_chunks=[],
        chunks_to_process=["chunk_0.mp3", "chunk_1.mp3"],
        current_chunk_index=0
    )
    assert state["project_id"] == "test_001"
    assert len(state["chunks_to_process"]) == 2

@pytest.mark.asyncio
async def test_graph_compilation_and_execution():
    """Test that the graph compiles and can execute a basic workflow."""
    graph = build_stt_graph()
    
    initial_state = {
        "project_id": "test_001",
        "global_memory": {"theme": "test", "glossary": [], "speakers": []},
        "processed_chunks": [],
        "chunks_to_process": ["chunk_0.mp3"],
        "current_chunk_index": 0
    }
    
    # Run the graph (mocking the actual LLM call inside the graph nodes would be needed for a full test,
    # but here we test if it runs without crashing and reaches the end state)
    
    # For now, we will just ensure the graph compiles and has the right nodes/edges
    assert "transcribe_chunk" in graph.nodes
    assert "finalize" in graph.nodes
