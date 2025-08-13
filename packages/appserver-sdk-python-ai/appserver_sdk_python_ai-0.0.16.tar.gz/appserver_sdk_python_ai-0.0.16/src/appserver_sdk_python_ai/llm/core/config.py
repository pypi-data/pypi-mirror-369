# appserver_sdk_python_ai/llm/core/config.py
"""
Configuração do módulo LLM
=========================

Define configurações e constantes para o módulo de LLM.
"""

from typing import Any

# Configurações padrão para LLM
DEFAULT_LLM_CONFIG = {
    "timeout": 30.0,
    "max_retries": 3,
    "retry_delay": 1.0,
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}


class LLMConfig:
    """Classe de configuração para LLM."""

    def __init__(self, **kwargs):
        """Inicializa a configuração com valores padrão e customizações."""
        self.config = DEFAULT_LLM_CONFIG.copy()
        self.config.update(kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração."""
        self.config[key] = value

    def update(self, config_dict: dict[str, Any]) -> None:
        """Atualiza múltiplos valores de configuração."""
        self.config.update(config_dict)

    def to_dict(self) -> dict[str, Any]:
        """Retorna a configuração como dicionário."""
        return dict(self.config)

    @property
    def timeout(self) -> float:
        """Timeout para requisições."""
        return float(self.config["timeout"])

    @property
    def max_retries(self) -> int:
        """Número máximo de tentativas."""
        return int(self.config["max_retries"])

    @property
    def max_tokens(self) -> int:
        """Número máximo de tokens."""
        return int(self.config["max_tokens"])

    @property
    def temperature(self) -> float:
        """Temperatura para geração."""
        return float(self.config["temperature"])
