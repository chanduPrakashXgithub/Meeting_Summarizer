
import pytest
from app.utils import extract_json

def test_extract_json_simple():
    text = 'prefix {"a":1, "b": [2,3]} suffix'
    parsed = extract_json(text)
    assert parsed['a'] == 1
    assert parsed['b'] == [2,3]
