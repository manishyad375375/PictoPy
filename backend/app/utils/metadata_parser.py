"""Utility functions for parsing image metadata."""
import json
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

def safe_json_parse(data: Union[str, dict, None]) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON data from various sources.
    
    Handles:
    - JSON strings from SQLite TEXT columns
    - Already-parsed dicts from PostgreSQL JSON columns
    - None/null values
    - Malformed JSON
    
    Args:
        data: String, dict, or None
        
    Returns:
        Parsed dictionary or None
        
    Examples:
        >>> safe_json_parse('{"camera":"Canon"}')
        {'camera': 'Canon'}
        
        >>> safe_json_parse({'camera': 'Canon'})
        {'camera': 'Canon'}
        
        >>> safe_json_parse('invalid')
        None
    """
    if data is None:
        return None
    
    # Already a dict
    if isinstance(data, dict):
        return data
    
    # Parse string
    if isinstance(data, str):
        # Empty string
        if not data.strip():
            return None
        
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                return parsed
            else:
                logger.warning(f"JSON parse resulted in non-dict: {type(parsed)}")
                return None
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON metadata: {e}")
            logger.debug(f"Invalid JSON content: {data[:100]}...")
            return None
    
    # Unexpected type
    logger.warning(f"Unexpected metadata type: {type(data)}")
    return None

def validate_metadata_schema(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata dictionary has expected structure.
    
    Args:
        metadata: Parsed metadata dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(metadata, dict):
        return False
    
    # Optional fields - any combination is valid
    valid_keys = {
        'camera', 'location', 'date_taken',
        'width', 'height', 'file_size',
        'format', 'exif', 'gps'
    }
    
    # Check all keys are valid
    for key in metadata.keys():
        if key not in valid_keys:
            logger.warning(f"Unknown metadata key: {key}")
    
    return True
