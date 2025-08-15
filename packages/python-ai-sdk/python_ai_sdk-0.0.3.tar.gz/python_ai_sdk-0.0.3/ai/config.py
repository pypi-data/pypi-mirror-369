"""
Configuration management for the AI SDK.

This module provides centralized configuration management for the AI SDK,
including retry policies, timeouts, and logging configuration.
"""

import logging
from typing import Optional
from dataclasses import dataclass


@dataclass
class AIConfig:
    """
    Configuration class for AI SDK settings.
    
    This class centralizes all configuration options for the AI SDK,
    making it easy to adjust behavior across the entire system.
    
    Attributes:
        max_retries (int): Maximum number of retry attempts for failed requests
        timeout (int): Request timeout in seconds
        rate_limit_delay (float): Base delay between rate-limited requests
        enable_logging (bool): Whether to enable SDK logging
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        max_tool_calls (int): Maximum recursive tool calls allowed
        stream_buffer_size (int): Buffer size for streaming responses
    """
    max_retries: int = 3
    timeout: int = 30
    rate_limit_delay: float = 1.0
    enable_logging: bool = True
    log_level: str = "INFO"
    max_tool_calls: int = 5
    stream_buffer_size: int = 1024

    def __post_init__(self):
        """Configure logging after initialization."""
        if self.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )


# Global configuration instance
_config = AIConfig()


def get_config() -> AIConfig:
    """
    Get the current global configuration.
    
    Returns:
        AIConfig: The current configuration instance
    """
    return _config


def set_config(config: AIConfig) -> None:
    """
    Set the global configuration.
    
    Args:
        config (AIConfig): New configuration to use
    """
    global _config
    _config = config


def update_config(**kwargs) -> None:
    """
    Update specific configuration values.
    
    Args:
        **kwargs: Configuration values to update
        
    Example:
        ```python
        update_config(max_retries=5, timeout=60)
        ```
    """
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")