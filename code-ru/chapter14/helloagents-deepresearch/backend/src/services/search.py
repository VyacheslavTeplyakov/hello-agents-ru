"""Вспомогательные функции поиска с использованием SearchTool из HelloAgents."""

from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

from hello_agents.tools import SearchTool

from config import Configuration
from utils import (
    deduplicate_and_format_sources,
    format_sources,
    get_config_value,
)

logger = logging.getLogger(__name__)

MAX_TOKENS_PER_SOURCE = 2000
_GLOBAL_SEARCH_TOOL = SearchTool(backend="hybrid")


def dispatch_search(
    query: str,
    config: Configuration,
    loop_count: int,
) -> Tuple[dict[str, Any] | None, list[str], Optional[str], str]:
    """Выполнить поиск через настроенный бэкенд и нормализовать ответ."""

    search_api = get_config_value(config.search_api)

    try:
        raw_response = _GLOBAL_SEARCH_TOOL.run(
            {
                "input": query,
                "backend": search_api,
                "mode": "structured",
                "fetch_full_page": config.fetch_full_page,
                "max_results": 5,
                "max_tokens_per_source": MAX_TOKENS_PER_SOURCE,
                "loop_count": loop_count,
            }
        )
    except Exception as exc:  # pragma: no cover - защитное логирование
        logger.exception("Поисковый бэкенд %s завершился ошибкой: %s", search_api, exc)
        raise

    if isinstance(raw_response, str):
        notices = [raw_response]
        logger.warning("Поисковый бэкенд %s вернул текстовое уведомление: %s", search_api, raw_response)
        payload: dict[str, Any] = {
            "results": [],
            "backend": search_api,
            "answer": None,
            "notices": notices,
        }
    else:
        payload = raw_response
        notices = list(payload.get("notices") or [])

    backend_label = str(payload.get("backend") or search_api)
    answer_text = payload.get("answer")
    results = payload.get("results", [])

    if notices:
        for notice in notices:
            logger.info("Уведомление поиска (%s): %s", backend_label, notice)

    logger.info(
        "Поиск: backend=%s resolved_backend=%s answer=%s results=%s",
        search_api,
        backend_label,
        bool(answer_text),
        len(results),
    )

    return payload, notices, answer_text, backend_label


def prepare_research_context(
    search_result: dict[str, Any] | None,
    answer_text: Optional[str],
    config: Configuration,
) -> tuple[str, str]:
    """Создать структурированный контекст и сводку источников для агентов."""

    sources_summary = format_sources(search_result)
    context = deduplicate_and_format_sources(
        search_result or {"results": []},
        max_tokens_per_source=MAX_TOKENS_PER_SOURCE,
        fetch_full_page=config.fetch_full_page,
    )

    if answer_text:
        context = f"Прямой ответ AI:\n{answer_text}\n\n{context}"

    return sources_summary, context
