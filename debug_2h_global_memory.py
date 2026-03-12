import asyncio
import os
import io
import json
import logging
import tempfile
from datasets import load_dataset
import soundfile as sf
import numpy as np
from pydub import AudioSegment

from app.gemini_client import GeminiClient
from app.global_memory_generator import GlobalMemoryGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_2h_global_memory_direct():
    logger.info("🚀 启动 2小时音频 Global Memory 直接测试 (Skip Full Norm)...")
    
    # 1. 配置本地客户端
    client = GeminiClient(
        api_key="123456", 
        model="gemini-3-flash-preview",
        use_inline_data=True
    )
    client.base_url = "http://localhost:8888/v1beta"
    client.is_local = True
    
    # 2. 抓取 2小时音频 (index_69)
    logger.info("正在从 Hugging Face 获取 index_69...")
    dataset = load_dataset("distil-whisper/earnings22", "full", split="test", streaming=True)
    
    target_item = None
    for idx, item in enumerate(dataset):
        if idx == 69:
            target_item = item
            break
            
    if not target_item:
        logger.error("未能找到 index_69 样本")
        return

    # 3. 极速转码 (仅转为 16kHz Mono，不进行复杂的 LUFS 计算)
    logger.info("执行极速转码 (16kHz Mono)...")
    raw_sr = target_item["audio"]["sampling_rate"]
    raw_array = target_item["audio"]["array"]
    
    # 转换为 int16 字节流直接给 pydub，避免 numpy 浮点运算
    samples = (raw_array * 32767).astype(np.int16)
    audio_segment = AudioSegment(
        samples.tobytes(), 
        frame_rate=raw_sr,
        sample_width=2, 
        channels=1
    )
    
    # 重采样并获取字节流
    audio_segment = audio_segment.set_frame_rate(16000)
    buffer = io.BytesIO()
    audio_segment.export(buffer, format="wav")
    audio_bytes = buffer.getvalue()
    
    logger.info(f"转码完成。体积: {len(audio_bytes)/1024/1024:.2f} MB, 时长: {len(audio_segment)/1000/60:.2f} 分钟")

    # 4. 调用 API
    logger.info("正在发送 Global Memory 请求...")
    generator = GlobalMemoryGenerator(client)
    
    try:
        global_memory = await generator.generate(audio_bytes, display_name="2H_DIRECT_TEST")
        print("\n✅ 成功！Global Memory 已生成：")
        print(json.dumps(global_memory, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_2h_global_memory_direct())
