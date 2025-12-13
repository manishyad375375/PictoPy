"""Tests for metadata parsing utilities."""
import pytest
import json
from app.utils.metadata_parser import safe_json_parse, validate_metadata_schema

def test_parse_json_string():
    """Test parsing valid JSON string."""
    input_str = '{"camera":"Canon EOS","location":"NYC"}'
    result = safe_json_parse(input_str)
    
    assert result is not None
    assert result['camera'] == 'Canon EOS'
    assert result['location'] == 'NYC'

def test_parse_already_dict():
    """Test handling of already-parsed dict."""
    input_dict = {'camera': 'Nikon', 'width': 1920}
    result = safe_json_parse(input_dict)
    
    assert result == input_dict

def test_parse_none():
    """Test handling of None input."""
    result = safe_json_parse(None)
    assert result is None

def test_parse_empty_string():
    """Test handling of empty string."""
    result = safe_json_parse('')
    assert result is None
    
    result = safe_json_parse('   ')
    assert result is None

def test_parse_invalid_json():
    """Test handling of malformed JSON."""
    invalid_inputs = [
        'not json at all',
        '{invalid}',
        '{"unclosed": ',
        '"just a string"',
    ]
    
    for invalid in invalid_inputs:
        result = safe_json_parse(invalid)
        assert result is None, f"Should return None for: {invalid}"

def test_parse_json_array():
    """Test handling of JSON array (not dict)."""
    result = safe_json_parse('[1,2,3]')
    assert result is None  # We expect dict, not array

def test_validate_metadata_valid():
    """Test validation of valid metadata."""
    valid_metadata = {
        'camera': 'Canon',
        'location': 'Paris',
        'width': 1920,
        'height': 1080,
    }
    
    assert validate_metadata_schema(valid_metadata) is True

def test_validate_metadata_empty():
    """Test validation of empty metadata."""
    assert validate_metadata_schema({}) is True

def test_validate_metadata_invalid_type():
    """Test validation rejects non-dict."""
    assert validate_metadata_schema([]) is False
    assert validate_metadata_schema("string") is False
    assert validate_metadata_schema(None) is False

def test_real_world_scenario():
    """Test real-world scenario from database."""
    # Simulating SQLite TEXT column
    db_value = json.dumps({
        'camera': 'iPhone 12',
        'location': 'San Francisco',
        'date_taken': '2025-12-13',
        'width': 4032,
        'height': 3024,
    })
    
    result = safe_json_parse(db_value)
    assert result is not None
    assert result['camera'] == 'iPhone 12'
    assert isinstance(result, dict)
