import asyncio
import os
import json
import logging
import random
import tempfile
import io
from datetime import datetime
from typing import List, Dict, Any

import evaluate
from datasets import load_dataset
import soundfile as sf
import numpy as np
from pydub import AudioSegment

from app.gemini_client import GeminiClient
from app.config import config
from app.utils import normalize_text, preprocess_audio, add_silence_padding
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

    async def run(self, take_samples: int = 3, target_sample_id: str = None):
        logger.info(f"Starting benchmark on {self.dataset_name}")
        clients = self._setup_clients()
        dataset = load_dataset(self.dataset_name, self.config_name, split=self.split, streaming=True)
        
        if target_sample_id:
            logger.info(f"Filtering for specific sample_id: {target_sample_id}")
            # Find the specific sample in the stream
            dataset_iter = iter(dataset)
            found = False
            for idx, item in enumerate(dataset_iter):
                if idx == 0:
                    logger.info(f"Available keys in dataset item: {item.keys()}")
                
                # Check various potential ID fields
                current_id = str(item.get("segment_id") or item.get("id") or idx)
                if current_id == target_sample_id:
                    dataset = [item]
                    found = True
                    break
            if not found:
                raise ValueError(f"Sample ID {target_sample_id} not found in dataset.")
        else:
            # Randomly sample by shuffling with a buffer
            dataset = dataset.shuffle(seed=random.randint(0, 1000), buffer_size=100).take(take_samples)
        
        self.metadata["samples_requested"] = take_samples if not target_sample_id else 1

        for idx, item in enumerate(dataset):
            raw_audio_array = item["audio"]["array"]
            raw_sample_rate = item["audio"]["sampling_rate"]
            reference = normalize_text(item.get("transcript") or item.get("text", ""))
            sample_id = item.get("segment_id") or f"sample_{idx}"
            
            logger.info(f"Processing sample {idx} ({sample_id})...")
            sample_data = {"id": idx, "sample_id": sample_id, "reference": reference}
            
            # Temporary file for the raw stream to allow preprocessing
            with tempfile.TemporaryDirectory() as temp_run_dir:
                raw_path = os.path.join(temp_run_dir, "raw_stream.wav")
                sf.write(raw_path, raw_audio_array, raw_sample_rate)
                
                # 1. Preprocess Global (High compression Opus for 100MB safety)
                logger.info(f"  Preprocessing global audio (High compression Opus)...")
                global_path = preprocess_audio(raw_path, mode="global")
                with open(global_path, "rb") as f:
                    global_audio_bytes = f.read()
                
                # 2. Preprocess Chunk (High clarity WAV)
                logger.info(f"  Preprocessing chunk audio (High clarity WAV)...")
                chunk_path = preprocess_audio(raw_path, mode="chunk")
                audio_segment_chunk = AudioSegment.from_file(chunk_path)
                
                # Update array and sample rate from normalized segment for VAD
                audio_array_np = np.array(audio_segment_chunk.get_array_of_samples()).astype(np.float32)
                max_val = float(2**(8 * audio_segment_chunk.sample_width - 1))
                audio_array_np = audio_array_np / max_val
                sample_rate = audio_segment_chunk.frame_rate

                # 3. Run VAD to get chunks from the high-clarity segment
                logger.info(f"  Running VAD and adding silence padding to chunks...")
                raw_chunks = self.vad.get_chunks(audio_array_np, sample_rate)
                chunk_paths = []
                for i, chunk_arr in enumerate(raw_chunks):
                    # Convert chunk back to AudioSegment to add padding
                    chunk_bytes = (chunk_arr * 32767).astype(np.int16).tobytes()
                    chunk_segment = AudioSegment(
                        chunk_bytes, 
                        frame_rate=sample_rate,
                        sample_width=2, 
                        channels=1
                    )
                    # Add 100ms padding
                    padded_chunk = add_silence_padding(chunk_segment, padding_ms=100)
                    
                    # Save to temp file for Graph
                    p = os.path.join(temp_run_dir, f"chunk_{i}.mp3")
                    padded_chunk.export(p, format="mp3")
                    chunk_paths.append(p)

                for client in clients:
                    model_id = client.model.replace("-", "_").replace(".", "_")
                    logger.info(f"  Running workflow for model: {client.model}")
                    
                    try:
                        global_gen = GlobalMemoryGenerator(client)
                        # Use compressed global audio for memory generation
                        global_memory = await global_gen.generate(global_audio_bytes, display_name=sample_id)
                        
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
    parser.add_argument("--sample-id", type=str, default=None, help="Target a specific sample ID.")
    args = parser.parse_args()
    
    benchmark = ASRBenchmark()
    asyncio.run(benchmark.run(take_samples=args.samples, target_sample_id=args.sample_id))
