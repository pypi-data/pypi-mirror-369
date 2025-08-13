"""Módulo LLM do AppServer SDK Python AI"""

import logging

__version__ = "1.0.0"

# Imports absolutos dentro do módulo
from appserver_sdk_python_ai.llm.core.enums import (
    ModelCapability,
    ModelProvider,
    ModelType,
    SupportedLanguage,
    TokenizationMethod,
)
from appserver_sdk_python_ai.llm.service.token_service import (
    get_model_info,
    get_portuguese_models,
    get_token_count,
    get_token_count_with_model,
    is_model_registered,
    list_available_models,
    register_custom_model,
)

# Importar funcionalidades comuns do módulo shared
from appserver_sdk_python_ai.shared import (
    DependencyChecker,
    HealthChecker,
    SDKLogger,
    VersionInfo,
)

from .exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMContentFilterError,
    LLMError,
    LLMInvalidInputError,
    LLMModelNotFoundError,
    LLMNetworkError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
    LLMStreamingError,
    LLMTimeoutError,
    LLMTokenLimitError,
    LLMValidationError,
)


def get_version_info():
    """Retorna informações sobre a versão e dependências."""
    return VersionInfo.create_version_info(
        module_name="llm",
        module_version=__version__,
        dependencies=check_dependencies(),
        additional_info={
            "available_models": len(list_available_models()),
            "portuguese_models": len(get_portuguese_models()),
        },
    )


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    return DependencyChecker.check_dependencies(
        ["tiktoken", "openai", "anthropic", "requests"]
    )


def health_check():
    """Verifica a saúde do módulo e suas dependências."""
    dependencies = check_dependencies()
    features = {
        "token_counting": True,
        "model_management": True,
        "portuguese_support": len(get_portuguese_models()) > 0,
        "custom_models": True,
    }

    return HealthChecker.create_health_report(
        module_name="llm",
        version=__version__,
        dependencies=dependencies,
        features=features,
        critical_deps=[],  # Nenhuma dependência é crítica por padrão
        optional_deps=["tiktoken", "openai", "anthropic", "requests"],
    )


def print_status():
    """Imprime status do módulo."""
    health = health_check()

    # Adicionar informações específicas do LLM
    print("=" * 60)
    print("MÓDULO LLM - appserver_sdk_python_ai")
    print("=" * 60)
    print(f"Versão: {__version__}")
    print(f"Status: {health['status']}")

    # Usar o método padrão para o resto
    HealthChecker.print_health_status(
        health, show_dependencies=True, show_features=True
    )

    # Informações adicionais específicas do LLM
    print("\n🤖 Informações dos modelos:")
    print(f"  • Total de modelos disponíveis: {len(list_available_models())}")
    print(f"  • Modelos com suporte ao português: {len(get_portuguese_models())}")

    print("\n📋 Provedores suportados:")
    providers = set()
    for model_info in list_available_models():
        if hasattr(model_info, "provider"):
            providers.add(model_info.provider.value)
    for provider in sorted(providers):
        print(f"  • {provider}")


def setup_logging(level=logging.INFO, format_string=None):
    """
    Configura logging para o módulo LLM.

    Args:
        level: Nível de logging
        format_string: Formato customizado para logs
    """
    return SDKLogger.setup_logging(
        level=level,
        format_string=format_string,
        logger_name="appserver_sdk_python_ai.llm",
    )


__all__ = [
    # Enums
    "ModelType",
    "ModelProvider",
    "ModelCapability",
    "TokenizationMethod",
    "SupportedLanguage",
    # Service
    "get_token_count",
    "get_token_count_with_model",
    "list_available_models",
    "get_model_info",
    "get_portuguese_models",
    "is_model_registered",
    "register_custom_model",
    # Exceptions
    "LLMError",
    "LLMProviderError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelNotFoundError",
    "LLMNetworkError",
    "LLMTokenLimitError",
    "LLMTimeoutError",
    "LLMValidationError",
    "LLMConfigurationError",
    "LLMInvalidInputError",
    "LLMResponseError",
    "LLMStreamingError",
    "LLMContentFilterError",
    # Funções de informação e status
    "get_version_info",
    "check_dependencies",
    "health_check",
    "print_status",
    "setup_logging",
    # Versão
    "__version__",
]
