"""Модуль LLM-сервиса"""

from hello_agents import HelloAgentsLLM
from ..config import get_settings

# Глобальный экземпляр LLM
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    Возвращает экземпляр LLM (одиночный объект)

    Returns:
        Экземпляр HelloAgentsLLM
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()

        # HelloAgentsLLM автоматически читает конфигурацию из переменных окружения
        # включая OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL и т.д.
        _llm_instance = HelloAgentsLLM()

        print(f"✅ LLM-сервис успешно инициализирован")
        print(f"   Провайдер: {_llm_instance.provider}")
        print(f"   Модель: {_llm_instance.model}")

    return _llm_instance


def reset_llm():
    """Сбрасывает экземпляр LLM (используется для тестирования или переконфигурации)"""
    global _llm_instance
    _llm_instance = None
