import os
import re
import subprocess
from datetime import datetime
from typing import List

def sort_audio_files(files: List[str]) -> List[str]:
    """
    Sorts files based on the pattern: 2026年01月26日 下午01点49分.m4a
    """
    # Regex to capture year, month, day, period (上午/下午), hour, and minute
    pattern = r"(\d{4})年(\d{2})月(\d{2})日\s+(上午|下午)(\d{2})点(\d{2})分"
    
    def get_time_key(filename):
        match = re.search(pattern, filename)
        if not match:
            return filename # Fallback
        
        y, m, d, period, h, mins = match.groups()
        h = int(h)
        if period == "下午" and h < 12:
            h += 12
        elif period == "上午" and h == 12:
            h = 0
            
        return datetime(int(y), int(m), int(d), h, int(mins))

    return sorted(files, key=get_time_key)

def merge_audio(input_dir: str, output_file: str):
    """
    Merges all .m4a files in input_dir into output_file using FFmpeg concat demuxer.
    """
    files = [f for f in os.listdir(input_dir) if f.endswith(".m4a") and not f.startswith("merged")]
    if not files:
        print("No audio files found to merge.")
        return

    sorted_files = sort_audio_files(files)
    print(f"Merging files in this order: {sorted_files}")

    # Create concat list for FFmpeg
    concat_list_path = os.path.join(input_dir, "ffmpeg_concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for filename in sorted_files:
            # Escape single quotes for FFmpeg
            escaped_name = filename.replace("'", "'\\''")
            f.write(f"file '{escaped_name}'\n")

    try:
        # Run FFmpeg concat
        # -y: overwrite output
        # -f concat: use concat demuxer
        # -safe 0: allow any filename
        # -c copy: copy streams without re-encoding
        command = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", concat_list_path, "-c", "copy", output_file
        ]
        subprocess.run(command, check=True)
        print(f"Successfully merged audio into {output_file}")
    finally:
        # Cleanup
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Merge audio segments in chronological order.")
    parser.add_argument("--input", default="data", help="Input directory containing audio segments.")
    parser.add_argument("--output", default="data/merged_full_audio.m4a", help="Path to the output merged file.")
    args = parser.parse_args()
    
    merge_audio(args.input, args.output)
