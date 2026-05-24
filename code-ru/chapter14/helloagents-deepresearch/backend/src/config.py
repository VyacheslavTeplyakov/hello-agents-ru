import os
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"
    ADVANCED = "advanced"


class Configuration(BaseModel):
    """Параметры конфигурации ассистента глубокого исследования."""

    max_web_research_loops: int = Field(
        default=3,
        title="Глубина исследования",
        description="Количество итераций поиска",
    )
    local_llm: str = Field(
        default="llama3.2",
        title="Название локальной модели",
        description="Название локально запущенной LLM (Ollama/LMStudio)",
    )
    llm_provider: str = Field(
        default="ollama",
        title="Провайдер LLM",
        description="Идентификатор провайдера (ollama, lmstudio или custom)",
    )
    search_api: SearchAPI = Field(
        default=SearchAPI.DUCKDUCKGO,
        title="Поисковый API",
        description="API для веб-поиска",
    )
    enable_notes: bool = Field(
        default=True,
        title="Включить заметки",
        description="Сохранять ли прогресс задач в NoteTool",
    )
    notes_workspace: str = Field(
        default="./notes",
        title="Рабочая директория заметок",
        description="Директория для хранения заметок NoteTool",
    )
    fetch_full_page: bool = Field(
        default=True,
        title="Загружать полную страницу",
        description="Включать полное содержимое страницы в результаты поиска",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        title="Базовый URL Ollama",
        description="Базовый URL для Ollama API (без суффикса /v1)",
    )
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        title="Базовый URL LMStudio",
        description="Базовый URL для OpenAI-совместимого API LMStudio",
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Удалять токены размышлений",
        description="Удалять ли теги <think> из ответов модели",
    )
    use_tool_calling: bool = Field(
        default=False,
        title="Использовать вызов инструментов",
        description="Использовать вызов инструментов вместо JSON-режима для структурированного вывода",
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        title="API-ключ LLM",
        description="Необязательный API-ключ для пользовательских OpenAI-совместимых сервисов",
    )
    llm_base_url: Optional[str] = Field(
        default=None,
        title="Базовый URL LLM",
        description="Необязательный базовый URL для пользовательских OpenAI-совместимых сервисов",
    )
    llm_model_id: Optional[str] = Field(
        default=None,
        title="Идентификатор модели LLM",
        description="Необязательный идентификатор модели для пользовательских OpenAI-совместимых сервисов",
    )

    @classmethod
    def from_env(cls, overrides: Optional[dict[str, Any]] = None) -> "Configuration":
        """Создать объект конфигурации из переменных окружения и переопределений."""

        raw_values: dict[str, Any] = {}

        # Загрузить значения из переменных окружения по именам полей
        for field_name in cls.model_fields.keys():
            env_key = field_name.upper()
            if env_key in os.environ:
                raw_values[field_name] = os.environ[env_key]

        # Дополнительные сопоставления для явных имён переменных окружения
        env_aliases = {
            "local_llm": os.getenv("LOCAL_LLM"),
            "llm_provider": os.getenv("LLM_PROVIDER"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "llm_model_id": os.getenv("LLM_MODEL_ID"),
            "llm_base_url": os.getenv("LLM_BASE_URL"),
            "lmstudio_base_url": os.getenv("LMSTUDIO_BASE_URL"),
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL"),
            "max_web_research_loops": os.getenv("MAX_WEB_RESEARCH_LOOPS"),
            "fetch_full_page": os.getenv("FETCH_FULL_PAGE"),
            "strip_thinking_tokens": os.getenv("STRIP_THINKING_TOKENS"),
            "use_tool_calling": os.getenv("USE_TOOL_CALLING"),
            "search_api": os.getenv("SEARCH_API"),
            "enable_notes": os.getenv("ENABLE_NOTES"),
            "notes_workspace": os.getenv("NOTES_WORKSPACE"),
        }

        for key, value in env_aliases.items():
            if value is not None:
                raw_values.setdefault(key, value)

        if overrides:
            for key, value in overrides.items():
                if value is not None:
                    raw_values[key] = value

        return cls(**raw_values)

    def sanitized_ollama_url(self) -> str:
        """Убедиться, что базовый URL Ollama содержит суффикс /v1, необходимый для OpenAI-клиентов."""

        base = self.ollama_base_url.rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return base

    def resolved_model(self) -> Optional[str]:
        """Наилучшее определение используемого идентификатора модели."""

        return self.llm_model_id or self.local_llm
