"""
Utility functions for the AI SDK.

This module provides common utility functions used throughout the AI SDK,
including validation, formatting, and helper functions.
"""

import base64
import json
import mimetypes
import asyncio
from typing import Any, Dict, List, Optional, Union
from ai.types import ValidationError
import logging

logger = logging.getLogger(__name__)


def validate_model_config(provider: str, model: str) -> None:
    """
    Validate model configuration for a given provider.
    
    Args:
        provider (str): The AI provider name
        model (str): The model identifier
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    if not provider:
        raise ValidationError("Provider name cannot be empty")
    
    if not model:
        raise ValidationError("Model name cannot be empty")
    
    # Provider-specific validation
    if provider == "openai":
        valid_models = [
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", 
            "text-embedding-3-small", "text-embedding-3-large"
        ]
        if not any(model.startswith(vm) for vm in valid_models):
            logger.warning(f"Unknown OpenAI model: {model}")
    
    elif provider == "google":
        valid_models = ["gemini-pro", "gemini-pro-vision", "text-embedding-004"]
        if not any(model.startswith(vm) for vm in valid_models):
            logger.warning(f"Unknown Google model: {model}")


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error messages consistently across the SDK.
    
    Args:
        error (Exception): The exception to format
        context (Optional[str]): Additional context about where the error occurred
        
    Returns:
        str: Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{context}: {error_type} - {error_msg}"
    else:
        return f"{error_type}: {error_msg}"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str (str): JSON string to parse
        default (Any): Default value if parsing fails
        
    Returns:
        Any: Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON with fallback.
    
    Args:
        obj (Any): Object to serialize
        default (str): Default JSON string if serialization fails
        
    Returns:
        str: JSON string or default value
    """
    try:
        return json.dumps(obj, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize to JSON: {e}")
        return default


def validate_base64(data: str) -> bool:
    """
    Validate if a string is valid base64.
    
    Args:
        data (str): String to validate
        
    Returns:
        bool: True if valid base64, False otherwise
    """
    try:
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False


def get_mime_type(filename: str) -> str:
    """
    Get MIME type for a filename.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        str: MIME type or 'application/octet-stream' as fallback
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


async def retry_with_backoff(
    func: callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func (callable): Function to retry
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Base delay between retries
        max_delay (float): Maximum delay between retries
        backoff_factor (float): Multiplier for exponential backoff
        
    Returns:
        Any: Result of the function call
        
    Raises:
        Exception: The last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                break
                
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            await asyncio.sleep(delay)
    
    raise last_exception


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length including suffix
        suffix (str): Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def clean_kwargs(**kwargs) -> Dict[str, Any]:
    """
    Remove None values from keyword arguments.
    
    Args:
        **kwargs: Keyword arguments to clean
        
    Returns:
        Dict[str, Any]: Cleaned dictionary without None values
    """
    return {k: v for k, v in kwargs.items() if v is not None}