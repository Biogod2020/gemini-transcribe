import asyncio
import os
import sys
from datasets import load_dataset

# Ensure app is in path
sys.path.append(os.getcwd())

from app.benchmark_orchestrator import BenchmarkOrchestrator

async def run_full_matrix():
    print("🌟 --- Initializing Full ASR Matrix Benchmark ---")
    
    # 1. Prepare Ground Truth (Sample 69)
    print("Loading Ground Truth from Earnings-22...")
    dataset = load_dataset("distil-whisper/earnings22", "full", split="test", streaming=True)
    
    target_index = 69
    reference_text = ""
    for idx, item in enumerate(dataset):
        if idx == target_index:
            reference_text = item.get("transcription", "")
            break
            
    if not reference_text:
        print("Error: Could not find ground truth.")
        return

    # 2. Define Matrix - Prioritize Baseline for fast results
    matrix = [
        {"model": "gemini-3.1-flash-lite-preview", "strategy": "baseline"},
        {"model": "gemini-3-flash-preview", "strategy": "baseline"},
        {"model": "gemini-3.1-flash-lite-preview", "strategy": "sota"},
        {"model": "gemini-3-flash-preview", "strategy": "sota"}
    ]
    
    # 3. Execute
    orchestrator = BenchmarkOrchestrator()
    results = await orchestrator.run_matrix(
        matrix=matrix,
        audio_path="data/raw/earnings22_2h.mp3",
        reference_text=reference_text,
        base_url="http://localhost:7861/unified/v1"
        # chunk_limit=3 # REMOVED FOR FULL TEST
    )
    
    # 4. Final Leaderboard Print
    print("\n" + "="*50)
    print("ASR PERFORMANCE LEADERBOARD (2h Sample)")
    print("="*50)
    print(f"{'Rank':<4} | {'Model':<30} | {'Strategy':<10} | {'Accuracy':<10} | {'Speed':<10}")
    print("-" * 75)
    
    sorted_results = sorted(results, key=lambda x: x["metrics"]["accuracy"], reverse=True)
    for i, res in enumerate(sorted_results):
        m = res["metrics"]
        v = res["variant"]
        print(f"{i+1:<4} | {v['model']:<30} | {v['strategy']:<10} | {m['accuracy']:.2f}% | {m['real_time_speed']:.1f}x")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_full_matrix())
