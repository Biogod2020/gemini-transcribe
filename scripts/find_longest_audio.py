from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_longest():
    logger.info("Loading Earnings-22 dataset (test split)...")
    dataset = load_dataset("distil-whisper/earnings22", "full", split="test", streaming=True)
    
    max_duration = 0
    longest_id = None
    
    logger.info("Scanning for longest file...")
    # We only need to check a few to get an idea, but let's try to find the real max
    # Earnings-22 has ~125 files
    for idx, item in enumerate(dataset):
        # audio['array'] length / sampling_rate = duration in seconds
        duration = len(item["audio"]["array"]) / item["audio"]["sampling_rate"]
        
        if duration > max_duration:
            max_duration = duration
            longest_id = item.get("segment_id") or f"index_{idx}"
            
        if (idx + 1) % 20 == 0:
            logger.info(f"Checked {idx+1} files. Current max: {max_duration/60:.2f} mins ({longest_id})")

    print(f"\n--- Result ---")
    print(f"Longest File ID: {longest_id}")
    print(f"Duration: {max_duration/60:.2f} minutes")
    print(f"Duration (seconds): {max_duration}")

if __name__ == "__main__":
    find_longest()
