
import json
import os

files = [
    "gemini-3.1-flash-lite-preview_sota_transcript.json",
    "gemini-3-flash-preview_sota_transcript.json",
    "gemini-3.1-flash-lite-preview_baseline_transcript.json",
    "gemini-3-flash-preview_baseline_transcript.json"
]

base_path = "/home/jiahao/code_workspace/gemini-transcribe/output/benchmarks/"

def audit_file(file_name):
    print(f"\n--- Auditing {file_name} ---")
    path = os.path.join(base_path, file_name)
    with open(path, 'r') as f:
        data = json.load(f)
    
    # 1. Missing Chunk Detection
    indices = [chunk.get('chunk_index') for chunk in data]
    indices.sort()
    
    missing = []
    # User asked for 0 to 35, but let's check what we have.
    for i in range(36):
        if i not in indices:
            missing.append(i)
    
    duplicates = [i for i in set(indices) if indices.count(i) > 1]
    
    if not missing and not duplicates and len(indices) == 36:
        print("Integrity Status: All 36 chunks present and sequential.")
    else:
        print(f"Integrity Status: Missing {missing}, Duplicates {duplicates}, Total count {len(indices)}")

    # Check first and last chunk info if raw_json is available
    if data:
        data.sort(key=lambda x: x.get('chunk_index'))
        first_chunk = data[0]
        last_chunk = data[-1]
        print(f"First chunk index: {first_chunk.get('chunk_index')}")
        print(f"Last chunk index: {last_chunk.get('chunk_index')}")

    # 2. Speaker Consistency Scan (SOTA only)
    is_sota = "sota" in file_name
    if is_sota:
        # Map of speaker names to the first chunk they appeared in
        speaker_first_seen = {}
        # All speaker names seen
        all_speakers_by_chunk = {}
        
        for chunk in data:
            idx = chunk.get('chunk_index')
            all_speakers_by_chunk[idx] = set()
            for entry in chunk.get('raw_json', []):
                sid = entry.get('speaker_id')
                if sid:
                    all_speakers_by_chunk[idx].add(sid)
                    if sid not in speaker_first_seen:
                        speaker_first_seen[sid] = idx
        
        initial_speakers = {s for s, idx in speaker_first_seen.items() if idx <= 5}
        print(f"Initial Speakers (0-5): {initial_speakers}")
        
        drifted = []
        for idx in sorted(all_speakers_by_chunk.keys()):
            if idx > 5:
                for sid in all_speakers_by_chunk[idx]:
                    if sid not in initial_speakers:
                        # Check for variations
                        matched = False
                        for base in initial_speakers:
                            # Heuristic for similarity
                            if not base or not sid: continue
                            # Remove titles for comparison
                            b_clean = base.lower().replace("mr.", "").replace("ms.", "").replace("mrs.", "").replace("(ceo)", "").strip()
                            s_clean = sid.lower().replace("mr.", "").replace("ms.", "").replace("mrs.", "").replace("(ceo)", "").strip()
                            
                            if b_clean in s_clean or s_clean in b_clean or (len(b_clean) > 3 and len(s_clean) > 3 and (b_clean.split()[-1] == s_clean.split()[-1])):
                                drifted.append((idx, base, sid))
                                matched = True
                                break
                        if not matched:
                            # Check against all previously seen speakers to catch chains
                            for prev_sid in speaker_first_seen:
                                if speaker_first_seen[prev_sid] < idx:
                                    ps_clean = prev_sid.lower().replace("mr.", "").strip()
                                    if s_clean in ps_clean or ps_clean in s_clean:
                                        # Only flag if it's a NEW variation
                                        if sid not in initial_speakers:
                                             # drifted.append((idx, prev_sid, sid))
                                             pass
        
        # Recalculate score based on how many chunks have drifted speakers
        chunks_with_drift = set(idx for idx, base, sid in drifted)
        total_chunks_after_5 = len([idx for idx in all_speakers_by_chunk if idx > 5])
        score = max(0, 100 * (1 - len(chunks_with_drift) / total_chunks_after_5)) if total_chunks_after_5 > 0 else 100
        
        print(f"Consistency Score: {score:.2f}%")
        print("Detailed Findings (Speaker Drift):")
        for idx, base, sid in drifted[:20]:
            print(f"  Chunk {idx}: '{base}' modified to '{sid}'")
        if len(drifted) > 20:
            print(f"  ... and {len(drifted) - 20} more")

    # 3. Chunk Content Continuity
    print("Detailed Findings (Continuity):")
    data_map = {chunk.get('chunk_index'): chunk for chunk in data}
    for i in range(2): # Check first two boundaries
        if i in data_map and i+1 in data_map:
            end_text = data_map[i].get('transcript', '')[-100:].replace('\n', ' ')
            start_text = data_map[i+1].get('transcript', '')[:100:].replace('\n', ' ')
            print(f"  Boundary {i}-{i+1}:")
            print(f"    End of {i}:   ...{end_text}")
            print(f"    Start of {i+1}: {start_text}...")
            
            # Heuristic for cut sentence
            if not end_text.strip().endswith('.') and not end_text.strip().endswith('?') and not end_text.strip().endswith('!'):
                print(f"    [!] Potential cut sentence at boundary {i}-{i+1}")

audit_file(files[0])
audit_file(files[1])
audit_file(files[2])
audit_file(files[3])
