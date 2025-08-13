# appserver_sdk_python_ai/webscraping/exceptions/__init__.py
"""
Exceções específicas para o módulo de WebScraping
===============================================

Este módulo define exceções customizadas para operações de web scraping.
"""

from .base import WebScrapingError
from .cache import CacheError
from .config import ScrapingConfigError
from .content import (
    ContentTooLargeError,
    ConversionError,
    JavaScriptError,
    ParsingError,
    RobotsTxtError,
    UnsupportedFormatError,
)
from .network import (
    AuthenticationError,
    NetworkError,
    ProxyError,
    RateLimitError,
    SSLVerificationError,
    TimeoutError,
)
from .validation import ValidationError

__all__ = [
    "WebScrapingError",
    "NetworkError",
    "TimeoutError",
    "AuthenticationError",
    "RateLimitError",
    "ProxyError",
    "SSLVerificationError",
    "ContentTooLargeError",
    "UnsupportedFormatError",
    "ConversionError",
    "JavaScriptError",
    "ParsingError",
    "RobotsTxtError",
    "ValidationError",
    "CacheError",
    "ScrapingConfigError",
]
