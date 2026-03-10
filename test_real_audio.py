import os
import asyncio
import argparse
from app.audio_exporter import AudioExporter
from app.vad_processor import VADProcessor
from app.gemini_client import GeminiClient
from app.global_memory_generator import GlobalMemoryGenerator
from app.graph import build_stt_graph
from app.config import config
from app.transcript_exporter import TranscriptExporter

async def main():
    parser = argparse.ArgumentParser(description="Run the Gemini Transcribe end-to-end test.")
    parser.add_argument(
        "--model", 
        type=str, 
        default=config.DEFAULT_MODEL,
        choices=config.AVAILABLE_MODELS,
        help=f"Select the model to use. Recommended choices: {', '.join(config.AVAILABLE_MODELS)}. Default is {config.DEFAULT_MODEL}."
    )
    parser.add_argument(
        "--chunk-len", 
        type=int, 
        default=3,
        choices=range(3, 8),
        help="Target length for each audio chunk in minutes (between 3 and 7). Default is 3 minutes."
    )
    parser.add_argument(
        "--use-local-proxy",
        action="store_true",
        help="Use local API endpoint at http://localhost:8888/v1beta and inlineData (bypasses File API)."
    )
    args = parser.parse_args()

    # 1. Configuration
    data_dir = "/home/jiahao/code_workspace/gemini-transcribe/data"
    output_dir = "/home/jiahao/code_workspace/gemini-transcribe/output"
    audio_file = os.path.join(data_dir, "2026年01月26日 下午02点18分.m4a")
    
    # Apply local proxy overrides if requested
    if args.use_local_proxy:
        config.BASE_URL = "http://localhost:8888/v1beta"
        config.API_KEY = "123456"
        config.USE_INLINE_DATA = True
    
    # API Key handling
    if config.API_KEY:
        api_key = config.API_KEY
    else:
        with open("/home/jiahao/code_workspace/gemini-transcribe/.env/geminiapikey.txt", "r") as f:
            api_key = f.read().strip()
    
    model_name = args.model
    target_chunk_sec = args.chunk_len * 60
    # Make the max duration slightly larger than target (e.g., target + 3 minutes) to allow flexibility for finding silence
    max_chunk_sec = target_chunk_sec + 180 
    
    print(f"--- Starting Test with {os.path.basename(audio_file)} ---")
    print(f"--- Model: {model_name} | Chunk Target: {args.chunk_len} mins ({target_chunk_sec}s) ---")
    
    # 2. VAD & Split (Phase 2)
    print("Loading audio and running VAD...")
    exporter = AudioExporter()
    samples, sr = exporter.load_audio(audio_file)
    
    vad = VADProcessor()
    # Chunking now uses limits selected by the user
    chunks = vad.get_chunks(samples, sampling_rate=sr, target_chunk_duration_sec=target_chunk_sec, max_chunk_duration_sec=max_chunk_sec)
    print(f"Generated {len(chunks)} chunks.")
    
    # Audio chunks still go to data/output_chunks for comparison if needed, 
    # but let's put them in output/chunks for the new flow
    audio_chunks_dir = os.path.join(output_dir, "audio_chunks")
    chunk_paths = exporter.export_chunks(chunks, audio_chunks_dir, prefix="chunk")
    
    # 3. Global Memory (Phase 3)
    print("Generating Global Memory...")
    client = GeminiClient(api_key=api_key, model=model_name, use_inline_data=config.USE_INLINE_DATA)
    gm_generator = GlobalMemoryGenerator(client)
    
    with open(audio_file, "rb") as f:
        audio_content = f.read()
    
    global_memory = await gm_generator.generate(audio_content, display_name="test_full_audio")
    print(f"Global Memory: {global_memory}")
    
    # 4. Transcription Loop (Phase 4)
    print("Starting Transcription Loop...")
    graph = build_stt_graph()
    
    # Project ID for filenames
    project_id = f"test_run_{model_name.replace('-', '_')}"
    
    initial_state = {
        "project_id": project_id,
        "global_memory": global_memory,
        "processed_chunks": [],
        "chunks_to_process": chunk_paths,
        "current_chunk_index": 0,
        "api_key": api_key,
        "model_name": model_name,
        "use_inline_data": config.USE_INLINE_DATA
    }
    
    final_state = await graph.ainvoke(initial_state)
    
    # 5. Export (Phase 5)
    print("\n--- Exporting Results ---")
    t_exporter = TranscriptExporter(output_dir=output_dir)
    json_path = t_exporter.export_json(project_id, final_state["global_memory"], final_state["processed_chunks"])
    md_path = t_exporter.export_markdown(project_id, final_state["global_memory"], final_state["processed_chunks"])
    
    print(f"JSON Export: {json_path}")
    print(f"Markdown Export: {md_path}")

    # 6. Result Summary
    print("\n--- Final Transcript Summary ---")
    for chunk in final_state["processed_chunks"]:
        print(f"Chunk {chunk['chunk_index']}:")
        print(chunk["transcript"])
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
