import pytest
from app.utils import normalize_text

def test_normalize_text_basic():
    text = "Hello, World!"
    assert normalize_text(text) == "hello world"

def test_normalize_text_punctuation():
    text = "This is a test. (With some punctuation!)"
    assert normalize_text(text) == "this is a test with some punctuation"

def test_normalize_text_spaces():
    text = "Too   many    spaces"
    assert normalize_text(text) == "too many spaces"

def test_normalize_text_empty():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""
