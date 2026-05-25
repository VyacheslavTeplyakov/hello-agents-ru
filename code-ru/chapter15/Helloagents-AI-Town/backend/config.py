"""Файл конфигурации"""

import os
from typing import Optional

class Settings:
    """Настройки приложения"""

    # Настройки API
    API_TITLE = "API кибер-городка"
    API_VERSION = "1.0.0"
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    # Настройки NPC
    NPC_UPDATE_INTERVAL = 30  # Интервал обновления состояния NPC (в секундах)

    # Настройки LLM (читаются из переменных окружения)
    # Фреймворк HelloAgents использует собственную конфигурацию LLM, OPENAI_API_KEY не нужен
    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-72B-Instruct")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api-inference.modelscope.cn/v1/")

    # Настройки CORS
    CORS_ORIGINS = ["*"]  # В продакшене ограничьте конкретными доменами

    @classmethod
    def validate(cls):
        """Проверяет корректность конфигурации"""
        if not cls.LLM_API_KEY:
            print("⚠️  Предупреждение: переменная LLM_API_KEY не задана")
            print("   Пропишите LLM_API_KEY в файле .env")
            print("   Пример: LLM_API_KEY=\"your-api-key\"")
            return False

        print(f"✅ Настройки LLM:")
        print(f"   Модель: {cls.LLM_MODEL_ID}")
        print(f"   Адрес сервиса: {cls.LLM_BASE_URL}")
        return True

settings = Settings()
