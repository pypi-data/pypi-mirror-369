"""
Logging utilities for the AI SDK.

This module provides structured logging capabilities for the AI SDK,
including request/response logging, performance metrics, and debugging tools.
"""

import logging
import time
import json
from typing import Any, Dict, Optional
from functools import wraps
from ai.config import get_config

# Create SDK-specific logger
sdk_logger = logging.getLogger("ai_sdk")


class SDKFormatter(logging.Formatter):
    """Custom formatter for SDK logs."""
    
    def format(self, record):
        # Add SDK-specific formatting
        if hasattr(record, 'provider'):
            record.msg = f"[{record.provider}] {record.msg}"
        
        if hasattr(record, 'model'):
            record.msg = f"[{record.model}] {record.msg}"
            
        return super().format(record)


def setup_logging():
    """Setup SDK logging configuration."""
    config = get_config()
    
    if not config.enable_logging:
        return
    
    # Create handler if it doesn't exist
    if not sdk_logger.handlers:
        handler = logging.StreamHandler()
        formatter = SDKFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        sdk_logger.addHandler(handler)
    
    sdk_logger.setLevel(getattr(logging, config.log_level.upper()))


def log_request(provider: str, model: str, **kwargs):
    """
    Log API request details.
    
    Args:
        provider (str): AI provider name
        model (str): Model name
        **kwargs: Additional request parameters
    """
    config = get_config()
    if not config.enable_logging:
        return
        
    # Sanitize sensitive data
    safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['api_key', 'token']}
    
    sdk_logger.info(
        f"API Request - Model: {model}, Params: {json.dumps(safe_kwargs, default=str)[:200]}",
        extra={'provider': provider, 'model': model}
    )


def log_response(provider: str, model: str, response_time: float, **kwargs):
    """
    Log API response details.
    
    Args:
        provider (str): AI provider name
        model (str): Model name
        response_time (float): Response time in seconds
        **kwargs: Additional response metadata
    """
    config = get_config()
    if not config.enable_logging:
        return
        
    sdk_logger.info(
        f"API Response - Time: {response_time:.2f}s, Metadata: {json.dumps(kwargs, default=str)[:200]}",
        extra={'provider': provider, 'model': model}
    )


def log_error(provider: str, model: str, error: Exception, **kwargs):
    """
    Log API errors.
    
    Args:
        provider (str): AI provider name
        model (str): Model name
        error (Exception): The error that occurred
        **kwargs: Additional error context
    """
    config = get_config()
    if not config.enable_logging:
        return
        
    sdk_logger.error(
        f"API Error - {type(error).__name__}: {str(error)}, Context: {json.dumps(kwargs, default=str)[:200]}",
        extra={'provider': provider, 'model': model},
        exc_info=True
    )


def log_tool_execution(tool_name: str, execution_time: float, success: bool, **kwargs):
    """
    Log tool execution details.
    
    Args:
        tool_name (str): Name of the executed tool
        execution_time (float): Execution time in seconds
        success (bool): Whether execution was successful
        **kwargs: Additional execution context
    """
    config = get_config()
    if not config.enable_logging:
        return
        
    level = logging.INFO if success else logging.WARNING
    status = "SUCCESS" if success else "FAILED"
    
    sdk_logger.log(
        level,
        f"Tool Execution - {tool_name}: {status} in {execution_time:.2f}s, Context: {json.dumps(kwargs, default=str)[:200]}"
    )


def performance_monitor(func):
    """
    Decorator to monitor function performance.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance logging
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            sdk_logger.debug(
                f"Function {func.__name__} completed in {execution_time:.2f}s"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            sdk_logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {e}"
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            sdk_logger.debug(
                f"Function {func.__name__} completed in {execution_time:.2f}s"
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            sdk_logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {e}"
            )
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# Initialize logging on module import
setup_logging()