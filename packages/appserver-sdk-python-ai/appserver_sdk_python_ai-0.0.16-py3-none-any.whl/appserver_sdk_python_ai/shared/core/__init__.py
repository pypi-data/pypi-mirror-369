"""Core functionality for the shared module."""

from .cache import (
    CacheError,
    FileCacheBackend,
    MemoryCacheBackend,
    UnifiedCacheManager,
    default_cache,
)
from .config import BaseConfig, ConfigManager
from .engines import (
    BaseEngine,
    EngineError,
    EngineInitializationError,
    EngineManager,
    EngineNotFoundError,
    EngineRegistry,
    EngineStatus,
    default_engine_manager,
    default_engine_registry,
)
from .logging import SDKLogger
from .network import (
    AsyncHTTPClient,
    HTTPClient,
    NetworkConfig,
    NetworkError,
    NetworkUtils,
    RateLimiter,
    RateLimitError,
    TimeoutError,
    URLBuilder,
    default_http_client,
    default_network_config,
)

# Standard configurations
from .standard_configs import (
    CacheStandardConfig,
    EngineStandardConfig,
    NetworkStandardConfig,
    ProcessingStandardConfig,
    SecurityStandardConfig,
    UnifiedModuleConfig,
    create_llm_config,
    create_module_config,
    create_ocr_config,
    create_webscraping_config,
)
from .validation import (
    COMMON_VALIDATORS,
    ChoiceValidator,
    CustomValidator,
    DataValidator,
    EmailValidator,
    LengthValidator,
    RangeValidator,
    RegexValidator,
    TypeValidator,
    URLValidator,
    ValidationRule,
    ValidationSchema,
)

__all__ = [
    # Original core
    "BaseConfig",
    "ConfigManager",
    "SDKLogger",
    # Cache system
    "UnifiedCacheManager",
    "MemoryCacheBackend",
    "FileCacheBackend",
    "CacheError",
    "default_cache",
    # Validation system
    "DataValidator",
    "ValidationSchema",
    "ValidationRule",
    "TypeValidator",
    "RangeValidator",
    "LengthValidator",
    "RegexValidator",
    "URLValidator",
    "EmailValidator",
    "ChoiceValidator",
    "CustomValidator",
    "COMMON_VALIDATORS",
    # Network system
    "HTTPClient",
    "AsyncHTTPClient",
    "NetworkConfig",
    "RateLimiter",
    "URLBuilder",
    "NetworkUtils",
    "NetworkError",
    "RateLimitError",
    "TimeoutError",
    "default_http_client",
    "default_network_config",
    # Engine management
    "BaseEngine",
    "EngineRegistry",
    "EngineManager",
    "EngineStatus",
    "EngineError",
    "EngineNotFoundError",
    "EngineInitializationError",
    "default_engine_registry",
    "default_engine_manager",
    # Standard configurations
    "NetworkStandardConfig",
    "CacheStandardConfig",
    "ProcessingStandardConfig",
    "SecurityStandardConfig",
    "EngineStandardConfig",
    "UnifiedModuleConfig",
    "create_module_config",
    "create_webscraping_config",
    "create_ocr_config",
    "create_llm_config",
]
