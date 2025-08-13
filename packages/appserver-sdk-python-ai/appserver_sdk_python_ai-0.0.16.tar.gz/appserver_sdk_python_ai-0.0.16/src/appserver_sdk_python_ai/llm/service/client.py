# appserver_sdk_python_ai/llm/service/client.py
"""
Cliente de serviço para LLM
==========================

Define cliente base para comunicação com provedores de LLM.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.config import LLMConfig
from ..exceptions import (
    LLMAuthenticationError,
    LLMProviderError,
)


class LLMClient(ABC):
    """Cliente base abstrato para provedores de LLM."""

    def __init__(self, config: LLMConfig | None = None):
        """Inicializa o cliente com configuração."""
        self.config = config or LLMConfig()
        self._authenticated = False

    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """Autentica com o provedor."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, model: str, **kwargs) -> dict[str, Any]:
        """Gera texto usando o modelo especificado."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """Lista modelos disponíveis."""
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> dict[str, Any]:
        """Obtém informações sobre um modelo."""
        pass

    def is_authenticated(self) -> bool:
        """Verifica se o cliente está autenticado."""
        return self._authenticated

    def health_check(self) -> dict[str, Any]:
        """Verifica a saúde da conexão com o provedor."""
        try:
            models = self.list_models()
            return {
                "status": "healthy",
                "authenticated": self.is_authenticated(),
                "models_available": len(models) > 0,
                "model_count": len(models),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self.is_authenticated(),
            }


class MockLLMClient(LLMClient):
    """Cliente mock para testes."""

    def __init__(self, config: LLMConfig | None = None):
        super().__init__(config)
        self._models = ["mock-model-1", "mock-model-2"]

    def authenticate(self, **kwargs) -> bool:
        """Mock de autenticação."""
        self._authenticated = True
        return True

    def generate_text(self, prompt: str, model: str, **kwargs) -> dict[str, Any]:
        """Mock de geração de texto."""
        if not self._authenticated:
            raise LLMAuthenticationError("Cliente não autenticado", "mock")

        if model not in self._models:
            raise LLMProviderError(f"Modelo {model} não encontrado", "mock")

        return {
            "text": f"Resposta mock para: {prompt}",
            "model": model,
            "tokens_used": len(prompt.split()) + 10,
            "provider": "mock",
        }

    def list_models(self) -> list[str]:
        """Lista modelos mock."""
        return self._models.copy()

    def get_model_info(self, model: str) -> dict[str, Any]:
        """Informações mock do modelo."""
        if model not in self._models:
            raise LLMProviderError(f"Modelo {model} não encontrado", "mock")

        return {
            "name": model,
            "provider": "mock",
            "max_tokens": 4096,
            "supports_streaming": True,
        }
