import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from scripts.benchmark import ASRBenchmark

@pytest.mark.asyncio
@patch('scripts.benchmark.load_dataset')
@patch('scripts.benchmark.evaluate.load')
@patch('scripts.benchmark.GeminiClient')
async def test_asr_benchmark_run(mock_client_class, mock_eval_load, mock_load_dataset):
    # Mock WER metric
    mock_wer = MagicMock()
    mock_wer.compute.return_value = 0.1
    mock_eval_load.return_value = mock_wer
    
    # Mock Dataset
    mock_item = {
        "audio": {"array": [0.1, 0.2], "sampling_rate": 16000},
        "text": "hello world"
    }
    mock_dataset = MagicMock()
    mock_dataset.__iter__.return_value = [mock_item]
    mock_dataset.take.return_value = mock_dataset
    mock_load_dataset.return_value = mock_dataset
    
    # Mock GeminiClient
    mock_client = mock_client_class.return_value
    mock_client.generate_content = AsyncMock(return_value={"data": "hello world", "thought": ""})
    mock_client.model = "test-model"
    
    # Run benchmark
    benchmark = ASRBenchmark()
    # Mock _save to avoid file I/O
    benchmark._save = MagicMock()
    
    results = await benchmark.run(take_samples=1)
    
    assert len(results["samples"]) == 1
    assert "test_model_wer" in results["summary"]
    assert results["summary"]["test_model_wer"] == 0.1
    benchmark._save.assert_called_once()
