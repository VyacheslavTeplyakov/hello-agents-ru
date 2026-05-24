"""Вспомогательные функции для координации инструкций по использованию инструмента заметок."""

from __future__ import annotations

import json

from models import TodoItem


def build_note_guidance(task: TodoItem) -> str:
    """Сгенерировать инструкции по использованию инструмента заметок для конкретной задачи."""

    tags_list = ["deep_research", f"task_{task.id}"]
    tags_literal = json.dumps(tags_list, ensure_ascii=False)

    if task.note_id:
        read_payload = json.dumps({"action": "read", "note_id": task.note_id}, ensure_ascii=False)
        update_payload = json.dumps(
            {
                "action": "update",
                "note_id": task.note_id,
                "task_id": task.id,
                "title": f"Задача {task.id}: {task.title}",
                "note_type": "task_state",
                "tags": tags_list,
                "content": "Добавить в обзор задачи информацию из текущего цикла",
            },
            ensure_ascii=False,
        )

        return (
            "Инструкции по работе с заметками:\n"
            f"- ID текущей заметки задачи: {task.note_id}.\n"
            f"- Перед написанием резюме необходимо вызвать: [TOOL_CALL:note:{read_payload}] для получения актуального содержимого.\n"
            f"- После анализа вызвать: [TOOL_CALL:note:{update_payload}] для синхронизации новой информации.\n"
            "- При обновлении сохранять существующую структуру абзацев, добавляя новое содержимое в соответствующие разделы.\n"
            f"- Рекомендуется сохранять tags как {tags_literal} для быстрого поиска другими агентами.\n"
            "- После успешной синхронизации с заметкой вывести резюме для пользователя.\n"
        )

    create_payload = json.dumps(
        {
            "action": "create",
            "task_id": task.id,
            "title": f"Задача {task.id}: {task.title}",
            "note_type": "task_state",
            "tags": tags_list,
            "content": "Записать обзор задачи и источники",
        },
        ensure_ascii=False,
    )

    return (
        "Инструкции по работе с заметками:\n"
        f"- Для данной задачи заметка ещё не создана. Сначала вызвать: [TOOL_CALL:note:{create_payload}].\n"
        "- После успешного создания записать возвращённый note_id и использовать его во всех последующих обновлениях.\n"
        "- После синхронизации с заметкой вывести резюме для пользователя.\n"
    )
