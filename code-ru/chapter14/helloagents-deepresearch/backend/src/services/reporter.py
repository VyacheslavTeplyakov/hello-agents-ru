"""Сервис, объединяющий результаты задач в итоговый отчёт."""

from __future__ import annotations

import json

from hello_agents import ToolAwareSimpleAgent

from models import SummaryState
from config import Configuration
from utils import strip_thinking_tokens
from services.text_processing import strip_tool_calls


class ReportingService:
    """Генерирует итоговый структурированный отчёт."""

    def __init__(self, report_agent: ToolAwareSimpleAgent, config: Configuration) -> None:
        self._agent = report_agent
        self._config = config

    def generate_report(self, state: SummaryState) -> str:
        """Сгенерировать структурированный отчёт на основе выполненных задач."""

        tasks_block = []
        for task in state.todo_items:
            summary_block = task.summary or "Информация отсутствует"
            sources_block = task.sources_summary or "Источники отсутствуют"
            tasks_block.append(
                f"### Задача {task.id}: {task.title}\n"
                f"- Цель задачи: {task.intent}\n"
                f"- Поисковый запрос: {task.query}\n"
                f"- Статус выполнения: {task.status}\n"
                f"- Резюме задачи:\n{summary_block}\n"
                f"- Обзор источников:\n{sources_block}\n"
            )

        note_references = []
        for task in state.todo_items:
            if task.note_id:
                note_references.append(
                    f"- Задача {task.id} «{task.title}»: note_id={task.note_id}"
                )

        notes_section = "\n".join(note_references) if note_references else "- Заметки задач отсутствуют"

        read_template = json.dumps({"action": "read", "note_id": "<note_id>"}, ensure_ascii=False)
        create_conclusion_template = json.dumps(
            {
                "action": "create",
                "title": f"Аналитический отчёт: {state.research_topic}",
                "note_type": "conclusion",
                "tags": ["deep_research", "report"],
                "content": "Записать здесь ключевые тезисы итогового отчёта",
            },
            ensure_ascii=False,
        )

        prompt = (
            f"Тема исследования: {state.research_topic}\n"
            f"Обзор задач:\n{''.join(tasks_block)}\n"
            f"Доступные заметки задач:\n{notes_section}\n"
            f"Для каждой заметки задачи используй формат: [TOOL_CALL:note:{read_template}] для чтения содержимого, затем объедини всю информацию и напиши отчёт.\n"
            f"Для сохранения итогового резюме можно вызвать: [TOOL_CALL:note:{create_conclusion_template}]"
        )

        response = self._agent.run(prompt)
        self._agent.clear_history()

        report_text = response.strip()
        if self._config.strip_thinking_tokens:
            report_text = strip_thinking_tokens(report_text)

        report_text = strip_tool_calls(report_text).strip()

        return report_text or "Генерация отчёта завершилась ошибкой, проверьте входные данные."
