"""
Пример базовых операций с NoteTool

Демонстрирует основные операции NoteTool:
1. Создание заметки (create)
2. Чтение заметки (read)
3. Обновление заметки (update)
4. Поиск заметок (search)
5. Список заметок (list)
6. Сводка заметок (summary)
7. Удаление заметки (delete)
"""

from hello_agents.tools import NoteTool
import re


def extract_note_id(output: str) -> str:
    """Извлекает note_id из текста вывода NoteTool"""
    match = re.search(r"ID:\s*(note_[0-9_]+)", output)
    if not match:
        raise ValueError(f"Не удалось извлечь note_id из вывода:\n{output}")
    return match.group(1)


def main():
    print("=" * 80)
    print("Пример базовых операций с NoteTool")
    print("=" * 80 + "\n")

    # Инициализация NoteTool
    notes = NoteTool(workspace="./project_notes")

    # 1. Создание заметки
    print("1. Создание заметки...")
    create_output_1 = notes.run({
        "action": "create",
        "title": "Рефакторинг проекта - Фаза 1",
        "content": """## Статус выполнения
Рефакторинг слоя модели данных завершён, покрытие тестами достигло 85%.

## Следующий шаг
Рефакторинг слоя бизнес-логики""",
        "note_type": "task_state",
        "tags": ["refactoring", "phase1"]
    })
    print(create_output_1 + "\n")
    note_id_1 = extract_note_id(create_output_1)

    # Создание второй заметки
    create_output_2 = notes.run({
        "action": "create",
        "title": "Проблема конфликта зависимостей",
        "content": """## Описание проблемы
Обнаружена несовместимость версий некоторых сторонних библиотек, требует решения.

## Затронутые области
3 модуля слоя бизнес-логики

## Следующий шаг
1. Использовать виртуальное окружение для изоляции
2. Зафиксировать версии
3. Использовать pipdeptree для анализа дерева зависимостей""",
        "note_type": "blocker",
        "tags": ["dependency", "urgent"]
    })
    print(create_output_2 + "\n")
    note_id_2 = extract_note_id(create_output_2)

    # 2. Чтение заметки
    print("2. Чтение заметки...")
    note_detail = notes.run({
        "action": "read",
        "note_id": note_id_1
    })
    print(note_detail + "\n")

    # 3. Обновление заметки
    print("3. Обновление заметки...")
    update_result = notes.run({
        "action": "update",
        "note_id": note_id_1,
        "content": """## Статус выполнения
Рефакторинг слоя модели данных завершён, покрытие тестами достигло 85%.

## Проблема
Обнаружен конфликт версий зависимостей, зафиксировано в отдельной заметке.

## Следующий шаг
Сначала решить конфликт зависимостей, затем продолжить рефакторинг слоя бизнес-логики"""
    })
    print(update_result + "\n")

    # 4. Поиск заметок
    print("4. Поиск заметок...")
    search_results = notes.run({
        "action": "search",
        "query": "зависимостей",
        "limit": 5
    })
    print(search_results + "\n")

    # 5. Список заметок
    print("5. Список всех заметок типа blocker...")
    blockers = notes.run({
        "action": "list",
        "note_type": "blocker",
        "limit": 10
    })
    print(blockers + "\n")

    # 6. Сводка заметок
    print("6. Генерация сводки заметок...")
    summary_output = notes.run({
        "action": "summary"
    })
    print(summary_output + "\n")

    # 7. Удаление заметки (демонстрация, при реальном использовании — осторожно)
    print("7. Удаление заметки (демонстрация)...")
    # delete_result = notes.run({
    #     "action": "delete",
    #     "note_id": note_id_2
    # })
    # print(delete_result + "\n")
    print(f"(Фактическое удаление пропущено, ID заметки: {note_id_2})\n")

    print("=" * 80)
    print("Демонстрация операций NoteTool завершена!")
    print("=" * 80)


if __name__ == "__main__":
    main()
