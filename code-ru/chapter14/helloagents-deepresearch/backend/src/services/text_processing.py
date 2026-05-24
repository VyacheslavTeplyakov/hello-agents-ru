"""Вспомогательные утилиты для нормализации текста, сгенерированного агентом."""

from __future__ import annotations

import re


def strip_tool_calls(text: str) -> str:
    """Удалить метки вызовов инструментов из текста."""

    if not text:
        return text

    pattern = re.compile(r"\[TOOL_CALL:[^\]]+\]")
    return pattern.sub("", text)
