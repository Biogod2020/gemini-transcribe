import asyncio
import os
import sys
import time

# Ensure app is in path
sys.path.append(os.getcwd())

from app.global_memory_generator import GlobalMemoryGenerator
from app.gemini_client import GeminiClient

async def simple_automated_benchmark():
    """
    Demonstrates the new Smart Orchestration:
    Just give it a file path, the App does the rest.
    """
    print("🚀 --- Starting Fully Automated Smart Summary Benchmark ---")
    start_time = time.time()
    
    # 1. Target: The 2h Earnings-22 sample
    raw_audio_path = "data/raw/earnings22_2h.mp3"
    
    # 2. Initialize
    client = GeminiClient(model="gemini-3.1-flash-lite-preview")
    generator = GlobalMemoryGenerator(client)
    
    # 3. One-shot Call (App internally handles Detect -> Transcode -> Summary)
    try:
        print(f"Calling App Core for: {raw_audio_path}")
        global_memory = await generator.generate(raw_audio_path)
        
        print("\n🏆 --- Smart Orchestration SUCCESS ---")
        import json
        print(json.dumps(global_memory, indent=2, ensure_ascii=False))
        
        duration = time.time() - start_time
        print(f"\nTotal Time: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ --- Benchmark FAILED ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_automated_benchmark())
