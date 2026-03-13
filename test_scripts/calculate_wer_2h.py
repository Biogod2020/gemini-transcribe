import json
import os
import sys
from datasets import load_dataset
import evaluate
from app.utils import normalize_text

def calculate_score():
    print("🚀 --- Calculating Accuracy Score (WER) for 2h Benchmark ---")
    
    # 1. Load generated transcript
    transcript_path = "output/proxy_2h_transcript.json"
    if not os.path.exists(transcript_path):
        print(f"Error: Transcript not found at {transcript_path}")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        processed_chunks = json.load(f)
    
    # Combine only the pure text from all chunks
    prediction_texts = []
    for chunk in processed_chunks:
        # If the transcript is a JSON-like string of speaker/text objects
        # We need to extract just the text. Our current transcript field
        # contains the formatted preview.
        # However, looking at the graph logic, we should use the parsed data.
        raw_json = chunk.get("raw_json", [])
        if isinstance(raw_json, list):
            for item in raw_json:
                prediction_texts.append(item.get("text", ""))
        else:
            # Fallback: if raw_json is missing, try to strip speaker prefixes from transcript
            import re
            clean_text = re.sub(r'^.*?: ', '', chunk.get("transcript", ""), flags=re.MULTILINE)
            prediction_texts.append(clean_text)
            
    prediction = " ".join(prediction_texts)
    
    # 2. Load Ground Truth from Earnings-22
    print("Fetching Ground Truth from Hugging Face...")
    dataset = load_dataset("distil-whisper/earnings22", "full", split="test", streaming=True)
    
    target_index = 69
    reference = ""
    print(f"Scanning dataset for index {target_index}...")
    for idx, item in enumerate(dataset):
        if idx % 10 == 0:
            print(f"Checking item {idx}...")
        if idx == target_index:
            print(f"Found match at index {idx}!")
            reference = item.get("transcription", "")
            break
    
    if not reference:
        print("Error: Could not find ground truth for index 69.")
        return

    # 3. Normalize both
    print("Normalizing text for fair comparison...")
    norm_prediction = normalize_text(prediction)
    norm_reference = normalize_text(reference)
    
    # 4. Calculate WER
    print("Computing Word Error Rate (WER)...")
    wer_metric = evaluate.load("wer")
    wer_score = wer_metric.compute(predictions=[norm_prediction], references=[norm_reference])
    
    accuracy = (1 - wer_score) * 100
    
    print("\n🏆 --- Benchmark Score Report ---")
    print(f"Model: Gemini 3.1 Flash Lite")
    print(f"WER: {wer_score:.4f} ({wer_score*100:.2f}%)")
    print(f"Accuracy Estimate: {accuracy:.2f}%")
    print("---------------------------------")
    
    # Save score
    score_report = {
        "model": "gemini-3.1-flash-lite-preview",
        "wer": wer_score,
        "accuracy": accuracy,
        "timestamp": os.popen("date").read().strip()
    }
    with open("output/benchmark_2h_score.json", "w") as f:
        json.dump(score_report, f, indent=2)

if __name__ == "__main__":
    calculate_score()
