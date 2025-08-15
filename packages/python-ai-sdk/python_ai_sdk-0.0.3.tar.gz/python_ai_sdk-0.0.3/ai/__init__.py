"""
Python AI SDK - A streaming-first AI SDK inspired by the Vercel AI SDK.

This package provides a unified interface for working with multiple AI providers
with a focus on streaming responses and strict typing.
"""

from ai.core import generateText, streamText, embed, embedMany
from ai.model import LanguageModel, openai, google, openai_embedding, google_embedding
from ai.tools import Tool
from ai.types import (
    TokenUsage,
    ReasoningDetail,
    OnFinish,
    OnFinishResult,
    FinishReason,
    AIError,
    APIError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    ToolExecutionError,
    ConfigurationError,
)
from ai.config import AIConfig, get_config, set_config, update_config
from ai.utils import (
    validate_model_config,
    format_error_message,
    safe_json_loads,
    safe_json_dumps,
    retry_with_backoff,
)

# Import image utilities if available
try:
    from ai.image import (
        image_from_file,
        image_from_url,
        image_from_base64,
        image_from_bytes,
        download_and_encode_image,
        create_image_message,
        text_with_image,
        text_with_url_image,
        file_from_path,
        file_from_bytes,
        download_file,
    )
    _HAS_IMAGE_UTILS = True
except ImportError:
    _HAS_IMAGE_UTILS = False

__version__ = "0.0.3"

# Base exports
__all__ = [
    # Core functions
    "generateText",
    "streamText",
    "embed", 
    "embedMany",
    # Classes
    "LanguageModel",
    "Tool",
    "AIConfig",
    # Model helpers
    "openai",
    "google",
    "openai_embedding",
    "google_embedding",
    # Configuration
    "get_config",
    "set_config", 
    "update_config",
    # Utilities
    "validate_model_config",
    "format_error_message",
    "safe_json_loads",
    "safe_json_dumps",
    "retry_with_backoff",
    # Types and Exceptions
    "TokenUsage",
    "ReasoningDetail", 
    "OnFinish",
    "OnFinishResult",
    "FinishReason",
    "AIError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError",
    "ToolExecutionError",
    "ConfigurationError",
]

# Add image utilities to exports if available
if _HAS_IMAGE_UTILS:
    __all__.extend([
        "image_from_file",
        "image_from_url", 
        "image_from_base64",
        "image_from_bytes",
        "download_and_encode_image",
        "create_image_message",
        "text_with_image",
        "text_with_url_image",
        "file_from_path",
        "file_from_bytes", 
        "download_file",
    ])