import asyncio
import os
import time
import json
from typing import List, Dict, Any, Literal
from app.config import config
from app.graph import build_stt_graph, STTState
from app.global_memory_generator import GlobalMemoryGenerator
from app.gemini_client import GeminiClient
from app.utils import get_overlapping_chunks, get_audio_duration
from app.metrics import MetricsCalculator

class BenchmarkOrchestrator:
    def __init__(self, output_dir: str = "output/benchmarks"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.metrics = MetricsCalculator()
        self.graph = build_stt_graph()

    async def run_variant(self, model: str, strategy: Literal["sota", "baseline"], audio_path: str, reference_text: str, base_url: str = None, chunk_limit: int = None) -> Dict[str, Any]:
        """Runs a single (Model, Strategy) benchmark variant."""
        print(f"\n🚀 --- Running Variant: Model={model}, Strategy={strategy} (Limit: {chunk_limit}) ---")
        start_time = time.time()
        
        # 1. Init Client
        client = GeminiClient(model=model, base_url=base_url, api_key="pwd") # Default proxy auth
        generator = GlobalMemoryGenerator(client)
        
        # 2. Global Memory (Skip if baseline)
        global_memory = {}
        if strategy == "sota":
            global_memory = await generator.generate(audio_path)
            
        # 3. Prepare Chunks
        chunks = await get_overlapping_chunks(audio_path, chunk_duration=240, overlap=0)
        if chunk_limit:
            chunks = chunks[:chunk_limit]
            
        # 4. Invoke Graph
        initial_state: STTState = {
            "project_id": f"bench_{strategy}_{int(time.time())}",
            "global_memory": global_memory,
            "processed_chunks": [],
            "chunks_to_process": chunks,
            "current_chunk_index": 0,
            "api_key": client.api_key,
            "model_name": client.model,
            "base_url": client.base_url,
            "use_inline_data": client.use_inline_data,
            "context_window_size": 2,
            "strategy": strategy
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        processing_time = time.time() - start_time
        
        # 5. Scoring
        prediction = " ".join([item.get("text", "") for chunk in final_state["processed_chunks"] for item in chunk.get("raw_json", [])])
        audio_duration = await get_audio_duration(audio_path)
        
        score = self.metrics.compute_all([prediction], [reference_text], audio_duration, processing_time)
        
        result = {
            "variant": {"model": model, "strategy": strategy},
            "metrics": score,
            "transcript_path": os.path.join(self.output_dir, f"{model}_{strategy}_transcript.json")
        }
        
        # Save transcript
        with open(result["transcript_path"], "w", encoding="utf-8") as f:
            json.dump(final_state["processed_chunks"], f, indent=2, ensure_ascii=False)
            
        return result

    async def run_matrix(self, matrix: List[Dict[str, Any]], audio_path: str, reference_text: str, base_url: str = None, chunk_limit: int = None):
        """Runs the full test matrix and generates a leaderboard."""
        results = []
        for item in matrix:
            res = await self.run_variant(item["model"], item["strategy"], audio_path, reference_text, base_url, chunk_limit=chunk_limit)
            results.append(res)
            
        # Generate Final Report
        report_path = os.path.join(self.output_dir, "matrix_report.json")
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"\n🏆 Matrix Benchmark Complete. Report saved to {report_path}")
        return results
