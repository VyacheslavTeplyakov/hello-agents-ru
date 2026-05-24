"""Модели состояния для рабочего процесса глубокого исследования."""

import operator
from dataclasses import dataclass, field
from typing import List, Optional

from typing_extensions import Annotated


@dataclass(kw_only=True)
class TodoItem:
    """Отдельный элемент списка задач."""

    id: int
    title: str
    intent: str
    query: str
    status: str = field(default="pending")
    summary: Optional[str] = field(default=None)
    sources_summary: Optional[str] = field(default=None)
    notices: list[str] = field(default_factory=list)
    note_id: Optional[str] = field(default=None)
    note_path: Optional[str] = field(default=None)
    stream_token: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)  # Тема отчёта
    search_query: str = field(default=None)  # Устаревший плейсхолдер
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # Счётчик итераций исследования
    running_summary: str = field(default=None)  # Устаревшее поле сводки
    todo_items: Annotated[list, operator.add] = field(default_factory=list)
    structured_report: Optional[str] = field(default=None)
    report_note_id: Optional[str] = field(default=None)
    report_note_path: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)  # Тема отчёта


@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None)  # Текст для обратной совместимости
    report_markdown: Optional[str] = field(default=None)
    todo_items: List[TodoItem] = field(default_factory=list)
