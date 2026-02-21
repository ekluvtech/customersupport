"""Helper utilities"""

import os
from typing import Any, Dict, Optional, List
from pathlib import Path


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default and required check
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raise error if not set
    
    Returns:
        Environment variable value or default
    
    Raises:
        ValueError: If required=True and variable is not set
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    
    return value


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries (later dicts override earlier ones)
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to only include specified keys
    
    Args:
        data: Dictionary to filter
        keys: List of keys to include
    
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in keys}


def exclude_dict_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to exclude specified keys
    
    Args:
        data: Dictionary to filter
        keys: List of keys to exclude
    
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k not in keys}


def deep_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation path
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found
    
    Returns:
        Value at path or default
    """
    keys = path.split(".")
    value = data
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    return sanitized

