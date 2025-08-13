# appserver_sdk_python_ai/ocr/exceptions/__init__.py
"""
Exceções específicas para o módulo de OCR
========================================

Este módulo define exceções customizadas para operações de OCR.
"""

from .base import OCRError
from .cache import OCRCacheError
from .config import OCRConfigurationError
from .engine import (
    OCREngineError,
    OCRNotAvailableError,
    OCRTimeoutError,
)
from .image import (
    OCRFormatNotSupportedError,
    OCRImageError,
    OCRLowConfidenceError,
)
from .network import OCRNetworkError

__all__ = [
    "OCRError",
    "OCRNotAvailableError",
    "OCREngineError",
    "OCRTimeoutError",
    "OCRImageError",
    "OCRFormatNotSupportedError",
    "OCRLowConfidenceError",
    "OCRCacheError",
    "OCRConfigurationError",
    "OCRNetworkError",
]
