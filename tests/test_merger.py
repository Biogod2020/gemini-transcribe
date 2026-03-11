import os
import pytest
from scripts.merge_audio import sort_audio_files

def test_sort_audio_files():
    """Test that audio files are correctly sorted by time in the filename."""
    files = [
        "2026年01月26日 下午03点07分.m4a",
        "2026年01月26日 下午01点49分.m4a",
        "2026年01月26日 下午02点18分.m4a",
        "2026年01月26日 下午02点05分.m4a"
    ]
    sorted_files = sort_audio_files(files)
    
    expected = [
        "2026年01月26日 下午01点49分.m4a",
        "2026年01月26日 下午02点05分.m4a",
        "2026年01月26日 下午02点18分.m4a",
        "2026年01月26日 下午03点07分.m4a"
    ]
    assert sorted_files == expected

def test_sort_audio_files_am_pm():
    """Test sorting with both AM and PM (if applicable, though project uses 下午)."""
    # Assuming the pattern handles 上午/下午 correctly
    files = [
        "2026年01月26日 下午01点00分.m4a",
        "2026年01月26日 上午11点00分.m4a",
    ]
    sorted_files = sort_audio_files(files)
    assert sorted_files[0] == "2026年01月26日 上午11点00分.m4a"
    assert sorted_files[1] == "2026年01月26日 下午01点00分.m4a"
