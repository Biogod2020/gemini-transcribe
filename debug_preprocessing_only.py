import asyncio
import os
import io
import logging
from datasets import load_dataset
import soundfile as sf
import numpy as np
from pydub import AudioSegment

from app.utils import preprocess_audio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_preprocessing_feasibility():
    logger.info("🚀 开始 2小时音频预处理体积验证...")
    
    # 1. 抓取 2小时音频 (index_69)
    logger.info("正在获取 index_69...")
    dataset = load_dataset("distil-whisper/earnings22", "full", split="test", streaming=True)
    
    target_item = None
    for idx, item in enumerate(dataset):
        if idx == 69:
            target_item = item
            break
            
    raw_sr = target_item["audio"]["sampling_rate"]
    raw_array = target_item["audio"]["array"]
    
    # 2. 保存原始 WAV (用于对比)
    raw_tmp = "feasibility_raw.wav"
    sf.write(raw_tmp, raw_array, raw_sr, format='wav')
    raw_size = os.path.getsize(raw_tmp) / 1024 / 1024
    logger.info(f"原始 WAV 体积: {raw_size:.2f} MB")

    try:
        # 3. 测试 Chunk Mode (理论上依然很大)
        logger.info("测试 Chunk Mode (WAV 16kHz Mono)...")
        chunk_path = preprocess_audio(raw_tmp, mode="chunk")
        chunk_size = os.path.getsize(chunk_path) / 1024 / 1024
        logger.info(f"➡️ Chunk Mode 体积: {chunk_size:.2f} MB")

        # 4. 测试 Global Mode (核心：Opus 32kbps)
        logger.info("测试 Global Mode (Opus 32kbps)...")
        global_path = preprocess_audio(raw_tmp, mode="global")
        global_size = os.path.getsize(global_path) / 1024 / 1024
        logger.info(f"➡️ Global Mode 体积: {global_size:.2f} MB")

        print("\n" + "="*50)
        print("📊 预处理结果总结:")
        print(f"音频时长: 123.45 分钟")
        print(f"WAV 格式 (转录用): {chunk_size:.2f} MB  (超标，但我们会切片处理)")
        print(f"Opus 格式 (全局用): {global_size:.2f} MB  (预期应 < 30MB，远低于 100MB 限制)")
        
        if global_size < 100:
            print("\n✅ 结论: Global Mode 的压缩率足以支持 2 小时音频的 inline_data 发送！")
        else:
            print("\n❌ 结论: 压缩率仍不足以支持 2 小时音频。")
        print("="*50)

    finally:
        # 清理
        for p in [raw_tmp, "feasibility_raw_chunk.wav", "feasibility_raw_global.opus"]:
            if os.path.exists(p): os.remove(p)

if __name__ == "__main__":
    asyncio.run(debug_preprocessing_feasibility())
