import asyncio
import os
import sys
import time
import json

# Ensure app is in path
sys.path.append(os.getcwd())

from app.gemini_client import GeminiClient
from app.global_memory_generator import GlobalMemoryGenerator
from app.graph import build_stt_graph, STTState
from app.utils import get_overlapping_chunks

async def local_proxy_benchmark_2h():
    """
    Test the full 2h flow using the gcli2api local proxy on port 7861.
    Uses gemini-3-flash-preview for maximum reasoning capability.
    """
    print("🚀 --- Phase 5: Start Local Proxy 2h Benchmark (localhost:7861) ---")
    start_time = time.time()
    
    # 1. Initialize Client for Local Proxy using Unified Endpoint
    client = GeminiClient(
        api_key="pwd", 
        model="gemini-3-flash-preview",
        base_url="http://localhost:7861/unified/v1"
    )
    
    generator = GlobalMemoryGenerator(client)
    graph = build_stt_graph()
    
    raw_audio_path = "data/raw/earnings22_2h.mp3"
    processed_file = "data/processed/earnings22_2h_summary_ready.mp3"

    try:
        # Step A: Global Memory
        print(f"\n[Proxy Call] Generating Global Memory for: {raw_audio_path}")
        global_memory = await generator.generate(raw_audio_path)
        print("Global Memory Acquired.")

        # Step B: Prepare Chunks (Using 4min blocks, ZERO overlap)
        print(f"\n[Proxy Call] Preparing seamless chunks (No overlap)...")
        stt_chunks = await get_overlapping_chunks(processed_file, chunk_duration=240, overlap=0)
        
        # Step C: Trigger Graph
        initial_state = {
            "project_id": "proxy_benchmark_2h",
            "global_memory": global_memory,
            "processed_chunks": [],
            "chunks_to_process": stt_chunks,
            "current_chunk_index": 0,
            "api_key": client.api_key,
            "model_name": client.model,
            "base_url": client.base_url, # Pass the proxy URL
            "use_inline_data": client.use_inline_data,
            "context_window_size": 2
        }
        
        print(f"\n[Proxy Call] Starting Transcription Loop for {len(stt_chunks)} chunks...")
        final_state = await graph.ainvoke(initial_state)
        
        # 3. Finalize
        print("\n🏆 --- Local Proxy 2h Benchmark SUCCESS ---")
        final_output_path = "output/proxy_2h_transcript.json"
        os.makedirs("output", exist_ok=True)
        
        with open(final_output_path, "w", encoding="utf-8") as f:
            json.dump(final_state["processed_chunks"], f, indent=2, ensure_ascii=False)
            
        duration = time.time() - start_time
        print(f"Result saved to: {final_output_path}")
        print(f"Total Time: {duration:.2f} seconds")

    except Exception as e:
        print(f"\n❌ --- Local Proxy Benchmark FAILED ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(local_proxy_benchmark_2h())
