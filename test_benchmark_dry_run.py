import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from scripts.benchmark import ASRBenchmark
import os
import json

async def test_benchmark_workflow_no_api():
    print("🚀 开始测试 Benchmark 完整流程（Mock API 模式）...")
    
    # 准备 Mock 数据
    mock_transcription = "this is a mock transcription"
    
    # 初始化 Benchmark (设置一个小样本量)
    benchmark = ASRBenchmark()
    
    # 关键：Mock GeminiClient 的 generate_content 方法
    # 让它返回模拟的成功响应
    mock_response = {
        "data": mock_transcription,
        "thought": "Thinking about the audio..."
    }
    
    with patch('app.gemini_client.GeminiClient.generate_content', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_response
        
        # 运行 Benchmark (只取 2 条数据)
        print("正在模拟运行（取 2 条样本）...")
        results = await benchmark.run(take_samples=2)
        
        # 验证结果
        print("\n--- 流程检查 ---")
        print(f"1. 样本处理数量: {len(results['samples'])}")
        print(f"2. 是否计算了平均 WER: {'summary' in results}")
        
        if len(results['samples']) == 2:
            print("✅ 数据集读取与循环逻辑正常。")
        
        # 检查是否生成了文件
        output_dir = "output/benchmarks"
        files = [f for f in os.listdir(output_dir) if f.startswith("benchmark_")]
        if files:
            print(f"✅ 结果持久化正常，最新文件: {max(files)}")
            
        print("\n--- 模拟响应内容检查 ---")
        for sample in results['samples']:
            print(f"Sample {sample['id']} Reference: {sample['reference']}")
            # 这里的键名是根据 model 自动生成的，例如 gemini_3_flash
            print(f"Sample {sample['id']} Prediction: {sample.get('gemini_3_flash', {}).get('prediction')}")

if __name__ == "__main__":
    asyncio.run(test_benchmark_workflow_no_api())
