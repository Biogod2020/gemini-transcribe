import os
import json
import shutil
import pytest
from app.transcript_exporter import TranscriptExporter

@pytest.fixture
def temp_output_dir():
    dir_path = "tests/temp_output"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    yield dir_path
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def test_export_json(temp_output_dir):
    exporter = TranscriptExporter(output_dir=temp_output_dir)
    project_id = "test_proj"
    global_memory = {"theme": "Test Theme", "speakers": [], "glossary": []}
    processed_chunks = [{"chunk_index": 0, "transcript": "S1: Hello", "raw_json": [{"speaker_id": "S1", "text": "Hello"}]}]
    
    path = exporter.export_json(project_id, global_memory, processed_chunks)
    
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["project_id"] == project_id
        assert data["processed_chunks"][0]["chunk_index"] == 0

def test_export_markdown(temp_output_dir):
    exporter = TranscriptExporter(output_dir=temp_output_dir)
    project_id = "test_proj"
    global_memory = {
        "theme": "Test Theme", 
        "tone": "Formal", 
        "narrative_structure": "Linear",
        "key_decisions": ["Decision 1"],
        "speakers": [{"id": "S1", "characteristics": "Clear voice"}],
        "glossary": ["Word1"]
    }
    processed_chunks = [{"chunk_index": 0, "transcript": "S1: Hello", "raw_json": [{"speaker_id": "S1", "text": "Hello"}]}]
    
    path = exporter.export_markdown(project_id, global_memory, processed_chunks)
    
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "# Transcription Report: test_proj" in content
        assert "**Theme**: Test Theme" in content
        assert "> **S1**: Hello" in content
