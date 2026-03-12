import asyncio
import os
import sys
from typing import Dict, Any

# Ensure app is in path
sys.path.append(os.getcwd())

from app.gemini_client import GeminiClient
from app.global_memory_generator import GlobalMemoryGenerator
from app.config import config

async def verify_2h_full_flow():
    """
    End-to-end verification script using the 2-hour preprocessed sample.
    This script tests if the existing app modules can correctly process
    the optimized 4.5MB Opus file and generate a Global Summary.
    """
    print("--- Phase 3: Full-Flow Verification (2h Sample) ---")
    
    # 1. Initialize Client and Generator
    # Use the default API key from .env/geminiapikey.txt if available
    client = GeminiClient()
    generator = GlobalMemoryGenerator(client)
    
    # 2. Locate the preprocessed file
    file_path = "data/processed/global_pass.opus"
    if not os.path.exists(file_path):
        print(f"Error: Preprocessed file not found at {file_path}")
        return

    print(f"Loading preprocessed audio: {file_path}")
    with open(file_path, "rb") as f:
        audio_content = f.read()
    
    print(f"Audio size: {len(audio_content) / 1024 / 1024:.2f} MB")
    
    # 3. Trigger Global Memory Generation
    print("Sending to Gemini for Global Summary (this may take 1-2 minutes)...")
    try:
        # Note: The existing GlobalMemoryGenerator.generate uploads the file
        # and then calls generate_content.
        summary = await generator.generate(
            audio_content=audio_content,
            display_name="earnings22_2h_global_pass"
        )
        
        print("\n--- Verification Result: SUCCESS ---")
        import json
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        
        # Basic validation of required fields
        required_fields = ["theme", "speakers", "glossary", "tone", "key_decisions", "narrative_structure"]
        missing = [f for f in required_fields if f not in summary]
        if missing:
            print(f"Warning: Missing expected fields in summary: {missing}")
        else:
            print("All expected fields are present.")
            
    except Exception as e:
        print(f"\n--- Verification Result: FAILED ---")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_2h_full_flow())
