# appserver_sdk_python_ai/llm/exceptions/__init__.py
"""
Exceções específicas para o módulo de LLM
========================================

Este módulo define exceções customizadas para operações de LLM.
"""

from .base import LLMError
from .provider import (
    LLMAuthenticationError,
    LLMModelNotFoundError,
    LLMNetworkError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMTokenLimitError,
)
from .response import LLMContentFilterError, LLMResponseError, LLMStreamingError
from .validation import LLMConfigurationError, LLMInvalidInputError, LLMValidationError

__all__ = [
    "LLMError",
    "LLMProviderError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelNotFoundError",
    "LLMNetworkError",
    "LLMTokenLimitError",
    "LLMTimeoutError",
    "LLMResponseError",
    "LLMStreamingError",
    "LLMContentFilterError",
    "LLMValidationError",
    "LLMConfigurationError",
    "LLMInvalidInputError",
]
