"""Модуль управления конфигурацией"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения
# Сначала пробуем загрузить .env из текущей директории
load_dotenv()

# Затем пробуем загрузить .env HelloAgents (если существует)
helloagents_env = Path(__file__).parent.parent.parent.parent / "HelloAgents" / ".env"
if helloagents_env.exists():
    load_dotenv(helloagents_env, override=False)  # Не перезаписываем уже установленные переменные


class Settings(BaseSettings):
    """Конфигурация приложения"""

    # Основные параметры приложения
    app_name: str = "HelloAgents Умный туристический помощник"
    app_version: str = "1.0.0"
    debug: bool = False

    # Настройки сервера
    host: str = "0.0.0.0"
    port: int = 8000

    # Настройки CORS — используем строку, разбиваем в коде
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # Настройки API карт AMap
    amap_api_key: str = ""

    # Настройки API Unsplash
    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""

    # Настройки LLM (читаются из переменных окружения, управляются HelloAgents)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"

    # Настройки журналирования
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорируем лишние переменные окружения

    def get_cors_origins_list(self) -> List[str]:
        """Возвращает список разрешённых CORS-источников"""
        return [origin.strip() for origin in self.cors_origins.split(',')]


# Создаём глобальный экземпляр конфигурации
settings = Settings()


def get_settings() -> Settings:
    """Возвращает экземпляр конфигурации"""
    return settings


# Проверяем обязательные параметры конфигурации
def validate_config():
    """Проверяет полноту конфигурации"""
    errors = []
    warnings = []

    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY не настроен")

    # HelloAgentsLLM автоматически читает LLM_API_KEY, OPENAI_API_KEY не обязателен
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM_API_KEY или OPENAI_API_KEY не настроены, LLM-функции могут быть недоступны")

    if errors:
        error_msg = "Ошибки конфигурации:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    if warnings:
        print("\n⚠️  Предупреждения конфигурации:")
        for w in warnings:
            print(f"  - {w}")

    return True


# Вывод информации о конфигурации (для отладки)
def print_config():
    """Печатает текущую конфигурацию (скрывая секретные данные)"""
    print(f"Название приложения: {settings.app_name}")
    print(f"Версия: {settings.app_version}")
    print(f"Сервер: {settings.host}:{settings.port}")
    print(f"API Key AMap: {'настроен' if settings.amap_api_key else 'не настроен'}")

    # Проверяем конфигурацию LLM
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL") or settings.openai_base_url
    llm_model = os.getenv("LLM_MODEL_ID") or settings.openai_model

    print(f"LLM API Key: {'настроен' if llm_api_key else 'не настроен'}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")
    print(f"Уровень журналирования: {settings.log_level}")
