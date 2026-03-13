import asyncio
import os
import sys
import time
import json
from typing import Dict, Any

# Ensure app is in path
sys.path.append(os.getcwd())

from app.config import config
from app.graph import build_stt_graph, STTState
from app.global_memory_generator import GlobalMemoryGenerator
from app.gemini_client import GeminiClient
from app.utils import get_overlapping_chunks

async def robust_stt_benchmark():
    """
    Directly calls the core Graph workflow without manual node control.
    Tests the system's true robustness and performance.
    """
    print("🚀 --- Phase 5: Start Robust 2h Benchmark (Pure Core Call) ---")
    start_time = time.time()
    
    raw_audio_path = "data/raw/earnings22_2h.mp3"
    
    # 1. Standard Initialization
    client = GeminiClient(model="gemini-3.1-flash-lite-preview")
    generator = GlobalMemoryGenerator(client)
    graph = build_stt_graph()
    
    try:
        # Step A: App-driven Global Memory
        print(f"\n[Core Call] Generating Global Memory for: {raw_audio_path}")
        global_memory = await generator.generate(raw_audio_path)
        
        # Step B: Prepare Chunks based on App config
        # Note: We still need to provide chunk paths to the graph as input
        # We use the standardized file path produced by the generator
        processed_file = "data/processed/earnings22_2h_summary_ready.mp3"
        
        print(f"\n[Core Call] Preparing overlapping chunks (4min per config)...")
        stt_chunks = await get_overlapping_chunks(
            processed_file, 
            chunk_duration=config.VAD_TARGET_CHUNK_SEC,
            overlap=30 # Fixed safety overlap
        )
        
        # Step C: Trigger Graph.ainvoke()
        initial_state = {
            "project_id": "robust_benchmark_2h",
            "global_memory": global_memory,
            "processed_chunks": [],
            "chunks_to_process": stt_chunks,
            "current_chunk_index": 0,
            "api_key": client.api_key,
            "model_name": client.model,
            "use_inline_data": client.use_inline_data,
            "context_window_size": 2 # System default
        }
        
        print(f"\n[Core Call] Starting LangGraph Workflow for {len(stt_chunks)} chunks...")
        # Pure core call - no manual while loop
        final_state = await graph.ainvoke(initial_state)
        
        # 3. Validation & Reporting
        print("\n🏆 --- Robust 2h Benchmark SUCCESS ---")
        final_output_path = "output/robust_2h_transcript.json"
        os.makedirs("output", exist_ok=True)
        
        with open(final_output_path, "w", encoding="utf-8") as f:
            json.dump(final_state["processed_chunks"], f, indent=2, ensure_ascii=False)
            
        duration = time.time() - start_time
        print(f"Full Result saved to: {final_output_path}")
        print(f"Total Time: {duration:.2f} seconds")
        print(f"Speed: {(7407/duration):.2f}x")

    except Exception as e:
        print(f"\n❌ --- Robust Benchmark CRASHED ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(robust_stt_benchmark())
