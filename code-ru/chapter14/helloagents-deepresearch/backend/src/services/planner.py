"""Сервис, преобразующий тему исследования в выполнимые задачи."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, List, Optional

from hello_agents import ToolAwareSimpleAgent

from models import SummaryState, TodoItem
from config import Configuration
from prompts import get_current_date, todo_planner_instructions
from utils import strip_thinking_tokens

logger = logging.getLogger(__name__)

TOOL_CALL_PATTERN = re.compile(
    r"\[TOOL_CALL:(?P<tool>[^:]+):(?P<body>[^\]]+)\]",
    re.IGNORECASE,
)

class PlanningService:
    """Обёртка над агентом-планировщиком для генерации структурированных задач."""

    def __init__(self, planner_agent: ToolAwareSimpleAgent, config: Configuration) -> None:
        self._agent = planner_agent
        self._config = config

    def plan_todo_list(self, state: SummaryState) -> List[TodoItem]:
        """Попросить агента-планировщика разбить тему на выполнимые задачи."""

        prompt = todo_planner_instructions.format(
            current_date=get_current_date(),
            research_topic=state.research_topic,
        )

        response = self._agent.run(prompt)
        self._agent.clear_history()

        logger.info("Необработанный вывод планировщика (усечён): %s", response[:500])

        tasks_payload = self._extract_tasks(response)
        todo_items: List[TodoItem] = []

        for idx, item in enumerate(tasks_payload, start=1):
            title = str(item.get("title") or f"Задача {idx}").strip()
            intent = str(item.get("intent") or "Ключевой вопрос по теме").strip()
            query = str(item.get("query") or state.research_topic).strip()

            if not query:
                query = state.research_topic

            task = TodoItem(
                id=idx,
                title=title,
                intent=intent,
                query=query,
            )
            todo_items.append(task)

        state.todo_items = todo_items

        titles = [task.title for task in todo_items]
        logger.info("Планировщик сгенерировал %d задач: %s", len(todo_items), titles)
        return todo_items

    @staticmethod
    def create_fallback_task(state: SummaryState) -> TodoItem:
        """Создать минимальную резервную задачу при неудаче планирования."""

        return TodoItem(
            id=1,
            title="Общий контекст темы",
            intent="Собрать основной контекст и последние события по теме",
            query=f"{state.research_topic} последние события" if state.research_topic else "Общий контекст темы",
        )

    # ------------------------------------------------------------------
    # Вспомогательные методы парсинга
    # ------------------------------------------------------------------
    def _extract_tasks(self, raw_response: str) -> List[dict[str, Any]]:
        """Разобрать вывод планировщика в список словарей задач."""

        text = raw_response.strip()
        if self._config.strip_thinking_tokens:
            text = strip_thinking_tokens(text)

        json_payload = self._extract_json_payload(text)
        tasks: List[dict[str, Any]] = []

        if isinstance(json_payload, dict):
            candidate = json_payload.get("tasks")
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, dict):
                        tasks.append(item)
        elif isinstance(json_payload, list):
            for item in json_payload:
                if isinstance(item, dict):
                    tasks.append(item)

        if not tasks:
            tool_payload = self._extract_tool_payload(text)
            if tool_payload and isinstance(tool_payload.get("tasks"), list):
                for item in tool_payload["tasks"]:
                    if isinstance(item, dict):
                        tasks.append(item)

        return tasks

    def _extract_json_payload(self, text: str) -> Optional[dict[str, Any] | list]:
        """Попытаться найти и разобрать JSON-объект или массив в тексте."""

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return None

        return None

    def _extract_tool_payload(self, text: str) -> Optional[dict[str, Any]]:
        """Разобрать первое выражение TOOL_CALL в выводе."""

        match = TOOL_CALL_PATTERN.search(text)
        if not match:
            return None

        body = match.group("body")

        try:
            payload = json.loads(body)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass

        parts = [segment.strip() for segment in body.split(",") if segment.strip()]
        payload: dict[str, Any] = {}
        for part in parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            payload[key.strip()] = value.strip().strip('"').strip("'")

        return payload or None
