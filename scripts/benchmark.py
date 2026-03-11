import asyncio
import os
import json
import logging
from datetime import datetime
import evaluate
from datasets import load_dataset
import soundfile as sf
import io
from typing import List, Dict, Any
from app.gemini_client import GeminiClient
from app.config import config
from app.utils import normalize_text

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASRBenchmark:
    def __init__(self, dataset_name: str = "librispeech_asr", split: str = "test", config_name: str = "clean"):
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

    def _setup_clients(self) -> List[GeminiClient]:
        """Initialize models for benchmarking."""
        # 1. Gemini 3 Flash (Local Proxy)
        client_flash = GeminiClient(
            api_key="123456", 
            model="gemini-3-flash-preview"
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
            model="gemini-3.1-flash-lite-preview"
        )
        
        return [client_flash, client_lite]

    def _prepare_audio(self, audio_array, sample_rate) -> bytes:
        """Convert array to WAV bytes."""
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, sample_rate, format='wav')
        return buffer.getvalue()

    async def run(self, take_samples: int = None):
        logger.info(f"Starting benchmark on {self.dataset_name}")
        clients = self._setup_clients()
        dataset = load_dataset(self.dataset_name, self.config_name, split=self.split, streaming=True)
        
        if take_samples:
            dataset = dataset.take(take_samples)
            self.metadata["samples_requested"] = take_samples

        for idx, item in enumerate(dataset):
            audio_bytes = self._prepare_audio(item["audio"]["array"], item["audio"]["sampling_rate"])
            reference = normalize_text(item["text"])
            
            logger.info(f"Processing sample {idx}...")
            
            # Parallel execution
            tasks = [
                client.generate_content(
                    prompt="Transcribe this audio precisely. Output ONLY the text.",
                    mime_type="audio/wav",
                    audio_content=audio_bytes
                ) for client in clients
            ]
            
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                sample_data = {"id": idx, "reference": reference}
                
                for i, client in enumerate(clients):
                    resp = responses[i]
                    model_id = client.model.replace("-", "_").replace(".", "_")
                    
                    if isinstance(resp, Exception):
                        logger.error(f"Model {client.model} failed on sample {idx}: {resp}")
                        sample_data[model_id] = {"error": str(resp)}
                    else:
                        pred = normalize_text(resp.get("data", ""))
                        sample_data[model_id] = {
                            "prediction": pred,
                            "wer": self.wer_metric.compute(predictions=[pred], references=[reference])
                        }
                
                self.results.append(sample_data)
                
            except Exception as e:
                logger.error(f"Unexpected error on sample {idx}: {e}")

        return self._finalize()

    def _finalize(self):
        """Compute aggregate metrics and save."""
        if not self.results:
            return {"error": "No results generated"}

        summary = {}
        # Get all model keys (excluding id and reference)
        model_keys = [k for k in self.results[0].keys() if k not in ["id", "reference"]]
        
        for key in model_keys:
            preds = [r[key]["prediction"] for r in self.results if "prediction" in r[key]]
            refs = [r["reference"] for r in self.results if "prediction" in r[key]]
            
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
    parser.add_argument("--samples", type=int, default=10)
    args = parser.parse_args()
    
    benchmark = ASRBenchmark()
    asyncio.run(benchmark.run(take_samples=args.samples))
