import asyncio
import os
import json
import logging
import random
import tempfile
from datetime import datetime
import evaluate
from datasets import load_dataset
import soundfile as sf
import io
import numpy as np
from typing import List, Dict, Any
from app.gemini_client import GeminiClient
from app.config import config
from app.utils import normalize_text
from app.vad_processor import VADProcessor
from app.global_memory_generator import GlobalMemoryGenerator
from app.graph import build_stt_graph

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASRBenchmark:
    def __init__(self, dataset_name: str = "distil-whisper/earnings22", split: str = "test", config_name: str = "full"):
        self.dataset_name = dataset_name
        self.split = split
        self.config_name = config_name
        self.wer_metric = evaluate.load("wer")
        self.results = []
        self.metadata = {
            "dataset": dataset_name,
            "config": config_name,
            "split": split,
            "timestamp": datetime.now().isoformat()
        }
        self.vad = VADProcessor()
        self.graph = build_stt_graph()

    def _setup_clients(self) -> List[GeminiClient]:
        """Initialize models for benchmarking."""
        # 1. Gemini 3 Flash (Local Proxy)
        client_flash = GeminiClient(
            api_key="123456", 
            model="gemini-3-flash-preview",
            use_inline_data=True
        )
        client_flash.base_url = "http://localhost:8888/v1beta"
        
        # 2. Gemini 3.1 Flash Lite (Official API)
        official_key = config.API_KEY
        if not official_key:
            try:
                with open(".env/geminiapikey.txt", "r") as f:
                    official_key = f.read().strip()
            except FileNotFoundError:
                logger.warning("Official API key not found. Lite results may fail.")
                
        client_lite = GeminiClient(
            api_key=official_key,
            model="gemini-3.1-flash-lite-preview",
            use_inline_data=True
        )
        
        return [client_flash, client_lite]

    def _prepare_audio_file(self, audio_array, sample_rate, temp_dir) -> str:
        """Save array to a temporary file and return path."""
        fd, path = tempfile.mkstemp(suffix=".mp3", dir=temp_dir)
        os.close(fd)
        # Convert to float32 for sf.write if necessary
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)
        sf.write(path, audio_array, sample_rate)
        return path

    async def run(self, take_samples: int = 3):
        logger.info(f"Starting benchmark on {self.dataset_name}")
        clients = self._setup_clients()
        dataset = load_dataset(self.dataset_name, self.config_name, split=self.split, streaming=True)
        
        # Randomly sample by shuffling with a buffer
        dataset = dataset.shuffle(seed=random.randint(0, 1000), buffer_size=100).take(take_samples)
        self.metadata["samples_requested"] = take_samples

        for idx, item in enumerate(dataset):
            audio_array = item["audio"]["array"]
            sample_rate = item["audio"]["sampling_rate"]
            # Some datasets use 'transcript' or 'text'
            reference = normalize_text(item.get("transcript") or item.get("text", ""))
            sample_id = item.get("segment_id") or f"sample_{idx}"
            
            logger.info(f"Processing sample {idx} ({sample_id})...")
            
            sample_data = {"id": idx, "sample_id": sample_id, "reference": reference}
            
            for client in clients:
                model_id = client.model.replace("-", "_").replace(".", "_")
                logger.info(f"  Running workflow for model: {client.model}")
                
                try:
                    # 1. Run VAD to get chunks
                    # Note: We need physical files for the Graph
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # VAD expects audio_data as np.ndarray
                        raw_chunks = self.vad.get_chunks(audio_array, sample_rate)
                        chunk_paths = []
                        for i, chunk_arr in enumerate(raw_chunks):
                            p = self._prepare_audio_file(chunk_arr, sample_rate, temp_dir)
                            chunk_paths.append(p)
                        
                        # 2. Generate Global Memory
                        # Convert full audio to bytes for Global Memory
                        buffer = io.BytesIO()
                        sf.write(buffer, audio_array, sample_rate, format='wav')
                        audio_bytes = buffer.getvalue()
                        
                        global_gen = GlobalMemoryGenerator(client)
                        global_memory = await global_gen.generate(audio_bytes, display_name=sample_id)
                        
                        # 3. Invoke Graph
                        initial_state = {
                            "project_id": f"bench_{sample_id}",
                            "global_memory": global_memory,
                            "processed_chunks": [],
                            "chunks_to_process": chunk_paths,
                            "current_chunk_index": 0,
                            "api_key": client.api_key,
                            "model_name": client.model,
                            "use_inline_data": client.use_inline_data
                        }
                        
                        final_state = await self.graph.ainvoke(initial_state)
                        
                        # 4. Concatenate result
                        full_prediction = " ".join([c["transcript"] for c in final_state["processed_chunks"]])
                        normalized_pred = normalize_text(full_prediction)
                        
                        sample_data[model_id] = {
                            "prediction": normalized_pred,
                            "wer": self.wer_metric.compute(predictions=[normalized_pred], references=[reference]),
                            "chunks": len(final_state["processed_chunks"])
                        }
                        
                except Exception as e:
                    logger.error(f"  Model {client.model} failed on sample {idx}: {e}")
                    sample_data[model_id] = {"error": str(e)}
            
            self.results.append(sample_data)

        return self._finalize()

    def _finalize(self):
        """Compute aggregate metrics and save."""
        if not self.results:
            return {"error": "No results generated"}

        summary = {}
        # Get model keys from the first sample that didn't error out entirely
        model_keys = []
        for r in self.results:
            keys = [k for k in r.keys() if k not in ["id", "sample_id", "reference"]]
            if keys:
                model_keys = keys
                break
        
        for key in model_keys:
            preds = [r[key]["prediction"] for r in self.results if key in r and "prediction" in r[key]]
            refs = [r["reference"] for r in self.results if key in r and "prediction" in r[key]]
            
            if preds:
                summary[f"{key}_wer"] = self.wer_metric.compute(predictions=preds, references=refs)

        final_output = {
            "metadata": self.metadata,
            "summary": summary,
            "samples": self.results
        }
        
        self._save(final_output)
        return final_output

    def _save(self, data):
        os.makedirs("output/benchmarks", exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"output/benchmarks/benchmark_{ts}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {filepath}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    
    benchmark = ASRBenchmark()
    asyncio.run(benchmark.run(take_samples=args.samples))
