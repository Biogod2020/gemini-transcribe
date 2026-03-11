import pytest
import asyncio
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock
from scripts.benchmark import ASRBenchmark

@pytest.mark.asyncio
@patch('scripts.benchmark.load_dataset')
@patch('scripts.benchmark.build_stt_graph')
@patch('scripts.benchmark.VADProcessor')
@patch('scripts.benchmark.GlobalMemoryGenerator')
async def test_asr_benchmark_uses_graph(mock_global_gen_class, mock_vad_class, mock_build_graph, mock_load_dataset):
    """
    Test that ASRBenchmark.run() correctly orchestrates VAD, Global Memory, and the LangGraph.
    """
    # 1. Mock Dataset
    mock_item = {
        "audio": {"array": np.array([0.1, 0.2], dtype=np.float32), "sampling_rate": 16000},
        "transcript": "official ground truth",
        "segment_id": "call_1"
    }
    mock_dataset = MagicMock()
    # Mock sampling 1 file
    mock_dataset.__iter__.return_value = [mock_item]
    mock_dataset.shuffle.return_value = mock_dataset
    mock_dataset.take.return_value = mock_dataset
    mock_load_dataset.return_value = mock_dataset
    
    # 2. Mock VAD
    mock_vad = mock_vad_class.return_value
    mock_vad.get_chunks.return_value = [np.array([0.1], dtype=np.float32), np.array([0.2], dtype=np.float32)]
    
    # 3. Mock Global Memory
    mock_global_gen = mock_global_gen_class.return_value
    mock_global_gen.generate = AsyncMock(return_value={"theme": "test theme"})
    
    # 4. Mock Graph
    mock_graph = AsyncMock()
    mock_graph.ainvoke.return_value = {
        "processed_chunks": [{"transcript": "model prediction"}]
    }
    mock_build_graph.return_value = mock_graph
    
    # Run benchmark
    benchmark = ASRBenchmark(dataset_name="distil-whisper/earnings22", config_name="full")
    benchmark._save = MagicMock() # Avoid file IO
    
    results = await benchmark.run(take_samples=1)
    
    # Verify Orchestration
    # Should call VAD
    assert mock_vad.get_chunks.called
    # Should call Global Memory
    assert mock_global_gen.generate.called
    # Should invoke Graph
    assert mock_graph.ainvoke.called
    
    # Verify results structure
    assert "summary" in results
    assert len(results["samples"]) == 1
    assert "gemini_3_flash_preview" in results["samples"][0]
    assert "gemini_3_1_flash_lite_preview" in results["samples"][0]
