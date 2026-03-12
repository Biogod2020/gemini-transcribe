import asyncio
import os
import sys
import time

# Ensure app is in path
sys.path.append(os.getcwd())

from app.gemini_client import GeminiClient
from app.global_memory_generator import GlobalMemoryGenerator
from app.utils import get_overlapping_chunks

async def verify_map_reduce_flow():
    print("🚀 --- Phase 3: Start 2h Sample Map-Reduce Verification ---")
    start_time = time.time()
    
    # 1. Inputs
    raw_audio = "data/raw/earnings22_2h.mp3"
    standardized_wav = "data/processed/full_standardized.wav"
    
    # 2. Standardization & Chunking (Should already be done, but let's ensure paths)
    if not os.path.exists(standardized_wav):
        print("Error: Please run scripts/fast_standardize.py first.")
        return

    print("Step 1: Chunking audio into overlapping segments...")
    # 30 min chunks, 2 min overlap
    chunks = await get_overlapping_chunks(standardized_wav, chunk_duration=1800, overlap=120)
    print(f"Total chunks to process: {len(chunks)}")

    # 3. Map-Reduce Execution
    client = GeminiClient()
    generator = GlobalMemoryGenerator(client)
    
    print("\nStep 2: Starting Parallel Map Phase (API Calls)...")
    try:
        final_summary = await generator.generate(chunks)
        
        print("\n🏆 --- Verification Result: SUCCESS ---")
        import json
        print(json.dumps(final_summary, indent=2, ensure_ascii=False))
        
        duration = time.time() - start_time
        print(f"\nTotal End-to-End Time: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ --- Verification Result: FAILED ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_map_reduce_flow())
