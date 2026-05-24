"""
Демонстрация трёхдневного рабочего процесса CodebaseMaintainer

Полная демонстрация рабочего процесса долгосрочного агента за три дня:
- День 1: Исследование кодовой базы (агент исследует самостоятельно)
- День 2: Анализ качества кода (агент анализирует самостоятельно)
- День 3: Планирование задач рефакторинга (агент планирует самостоятельно)
- Через неделю: Проверка прогресса

"""

import os
# Настройка модели эмбеддинга (выберите один из вариантов)
# Вариант 1: TF-IDF (простейший, без дополнительных зависимостей)
os.environ['EMBED_MODEL_TYPE'] = 'tfidf'
os.environ['EMBED_MODEL_NAME'] = ''  # Важно: должна быть пустой строкой, иначе передаются несовместимые параметры
from dotenv import load_dotenv
load_dotenv()
# Вариант 2: Локальный Transformer (требуется: pip install sentence-transformers и HF-токен)
# os.environ['EMBED_MODEL_TYPE'] = 'local'
# os.environ['EMBED_MODEL_NAME'] = 'sentence-transformers/all-MiniLM-L6-v2'
# os.environ['HF_TOKEN'] = 'your_hf_token_here'  # или используйте huggingface-cli login
# Вариант 3: DashScope (требуется API-ключ)
# os.environ['EMBED_MODEL_TYPE'] = 'dashscope'
# os.environ['EMBED_MODEL_NAME'] = 'text-embedding-v3'
# os.environ['EMBED_API_KEY'] = 'your_api_key_here'

from hello_agents import HelloAgentsLLM
from datetime import datetime
import json
import time

# Импорт CodebaseMaintainer
import sys
sys.path.append('.')
from codebase_maintainer import CodebaseMaintainer


def day_1_exploration(maintainer):
    """День 1: Исследование кодовой базы (агентный режим)

    На этом этапе мы даём агенту только высокоуровневую цель,
    агент самостоятельно решает:
    - какие shell-команды использовать для исследования кодовой базы
    - какие файлы просматривать
    - нужно ли делать заметки
    """
    print("\n" + "=" * 80)
    print("День 1: Исследование кодовой базы (агент исследует самостоятельно)")
    print("=" * 80 + "\n")

    # 1. Первичное исследование — агент самостоятельно решает, как исследовать
    print("### 1. Первичное исследование структуры проекта ###")
    print("Подсказка: агент самостоятельно выберет команды (например, find, ls, cat)\n")
    response = maintainer.explore()
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # 2. Углублённый анализ модуля — агент самостоятельно выбирает метод анализа
    print("### 2. Анализ модуля обработки данных ###")
    print("Подсказка: агент самостоятельно решит, как анализировать этот файл\n")
    response = maintainer.run("Пожалуйста, просмотрите файл data_processor.py и проанализируйте его архитектуру")
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # Имитация течения времени
    time.sleep(1)


def day_2_analysis(maintainer):
    """День 2: Анализ качества кода (агентный режим)

    Агент самостоятельно решает:
    - какими методами анализировать качество кода (grep TODO? подсчёт строк? проверка сложности?)
    - нужно ли создавать заметки для фиксации проблем
    - как организовать результаты анализа
    """
    print("\n" + "=" * 80)
    print("День 2: Анализ качества кода (агент анализирует самостоятельно)")
    print("=" * 80 + "\n")

    # 1. Общий анализ качества — агент самостоятельно выбирает метод
    print("### 1. Анализ качества кода ###")
    print("Подсказка: агент самостоятельно решит, как анализировать (например, grep TODO, wc -l, анализ сложности)\n")
    response = maintainer.analyze()
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # 2. Проверка конкретных проблем — агент углублённо анализирует самостоятельно
    print("### 2. Анализ кода API-клиента ###")
    print("Подсказка: агент самостоятельно решит, как оценить качество этого файла\n")
    response = maintainer.run(
        "Пожалуйста, проанализируйте качество кода api_client.py, особенно обработку ошибок, и дайте рекомендации по улучшению"
    )
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # Имитация течения времени
    time.sleep(1)


def day_3_planning(maintainer):
    """День 3: Планирование задач рефакторинга (агентный режим)

    Агент самостоятельно решает:
    - какие исторические заметки просматривать
    - как организовать планирование задач
    - нужно ли создавать новые заметки
    - как расставить приоритеты
    """
    print("\n" + "=" * 80)
    print("День 3: Планирование задач рефакторинга (агент планирует самостоятельно)")
    print("=" * 80 + "\n")

    # 1. Обзор прогресса — агент самостоятельно просматривает заметки и планирует
    print("### 1. Обзор текущего прогресса и планирование следующих шагов ###")
    print("Подсказка: агент самостоятельно просмотрит исторические заметки, проанализирует текущий прогресс и составит план\n")
    response = maintainer.plan_next_steps()
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # 2. Запрос агенту создать детальный план (агент самостоятельно решит, использовать ли NoteTool)
    print("### 2. Поручить агенту создать детальный план рефакторинга ###")
    print("Подсказка: агент самостоятельно решит, как создать и организовать план рефакторинга\n")
    response = maintainer.run(
        "На основе нашего анализа создайте детальный план рефакторинга на эту неделю. "
        "План должен включать: цели, список конкретных задач, расписание и риски. "
        "Пожалуйста, используйте NoteTool для создания заметки типа task_state для фиксации этого плана."
    )
    print(f"\nРезюме помощника:\n{response[:500]}...\n")

    # Имитация течения времени
    time.sleep(1)


def week_later_review(maintainer):
    """Через неделю: проверка прогресса"""
    print("\n" + "=" * 80)
    print("Через неделю: проверка прогресса")
    print("=" * 80 + "\n")

    # 1. Просмотр сводки заметок
    print("### 1. Сводка заметок ###")
    summary = maintainer.note_tool.run({"action": "summary"})
    print("Сводка заметок:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print()

    # 2. Генерация полного отчёта
    print("### 2. Отчёт о сессии ###")
    report = maintainer.generate_report()
    print("\nОтчёт о сессии:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def demonstrate_cross_session_continuity():
    """Демонстрация непрерывности между сессиями"""
    print("\n" + "=" * 80)
    print("Демонстрация непрерывности между сессиями")
    print("=" * 80 + "\n")

    # Первая сессия
    print("### Первая сессия (session_1) ###")
    maintainer_1 = CodebaseMaintainer(
        project_name="demo_codebase",
        # При реальном использовании замените на актуальный путь к коду
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # Создание нескольких заметок
    maintainer_1.create_note(
        title="Проблемы качества кода",
        content="Обнаружено несколько комментариев TODO, требующих реализации, особенно в части валидации данных и обработки ошибок",
        note_type="blocker",
        tags=["quality", "urgent"]
    )

    stats_1 = maintainer_1.get_stats()
    print(f"Статистика сессии 1: {stats_1['activity']}\n")

    # Имитация завершения сессии
    time.sleep(1)

    # Вторая сессия (новый ID сессии, но заметки сохранены)
    print("### Вторая сессия (session_2) ###")
    maintainer_2 = CodebaseMaintainer(
        project_name="demo_codebase",  # тот же проект
        # При реальном использовании замените на актуальный путь к коду
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # Поиск предыдущих заметок
    response = maintainer_2.run(
        "Какие проблемы качества кода мы обнаружили ранее? Каким из них следует уделить приоритетное внимание?"
    )
    print(f"\nОтвет помощника:\n{response[:300]}...\n")

    stats_2 = maintainer_2.get_stats()
    print(f"Статистика сессии 2: {stats_2['activity']}\n")

    # Отображение сводки заметок
    summary = maintainer_2.note_tool.run({"action": "summary"})
    print("Сводка заметок между сессиями:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def demonstrate_tool_synergy():
    """Демонстрация синергии трёх инструментов (агентный режим)

    В этой демонстрации:
    - мы не вызываем инструменты вручную
    - а позволяем агенту самостоятельно решать, какие инструменты использовать
    - агент автоматически координирует использование нескольких инструментов в зависимости от задачи
    """
    print("\n" + "=" * 80)
    print("Демонстрация синергии трёх инструментов (агент координирует самостоятельно)")
    print("=" * 80 + "\n")

    maintainer = CodebaseMaintainer(
        project_name="synergy_demo",
        # При реальном использовании замените на актуальный путь к коду
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # Агент самостоятельно анализирует и записывает результаты
    print("### Агент самостоятельно анализирует TODO в кодовой базе ###")
    print("Подсказка: агент самостоятельно решит:\n")
    print("   1. Использовать TerminalTool для поиска TODO")
    print("   2. Использовать NoteTool для записи обнаружений")
    print("   3. Использовать MemoryTool для запоминания ключевой информации\n")

    response = maintainer.run(
        "Пожалуйста, проанализируйте все TODO в кодовой базе и запишите обнаружения в заметки. "
        "Затем скажите, какие функции следует реализовать в первую очередь."
    )
    print(f"Ответ помощника:\n{response[:500]}...\n")

    # Отображение статистики
    stats = maintainer.get_stats()
    print("Статистика использования инструментов:")
    print(f"  - Количество вызовов инструментов: {stats['activity']['tool_calls']}")
    print(f"  - Выполненные команды: {stats['activity']['commands_executed']}")
    print(f"  - Созданные заметки: {stats['activity']['notes_created']}")


def main():
    """Главная функция"""
    print("=" * 80)
    print("Демонстрация трёхдневного рабочего процесса CodebaseMaintainer (агентная версия)")
    print("=" * 80)

    print("\nКлючевая особенность: агент принимает решения самостоятельно")
    print("Используем пример кодовой базы, созданной в главе 9")
    print("Путь к кодовой базе: ./codebase")
    print("Включённые файлы: data_processor.py, api_client.py, utils.py, models.py")
    print("\nДоступные инструменты агента:")
    print("   - TerminalTool: выполнение shell-команд")
    print("   - NoteTool: создание и управление заметками")
    print("   - MemoryTool: управление памятью")
    print("\nАгент самостоятельно решает:")
    print("   - какие инструменты использовать")
    print("   - какие команды выполнять")
    print("   - как организовать информацию\n")

    # Инициализация помощника
    maintainer = CodebaseMaintainer(
        project_name="demo_codebase",
        # При реальном использовании замените на актуальный путь к коду
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # Выполнение трёхдневного рабочего процесса
    day_1_exploration(maintainer)
    day_2_analysis(maintainer)
    day_3_planning(maintainer)
    week_later_review(maintainer)

    # Дополнительные демонстрации
    print("\n\n" + "=" * 80)
    print("Дополнительные демонстрации")
    print("=" * 80)

    demonstrate_cross_session_continuity()
    demonstrate_tool_synergy()

    print("\n" + "=" * 80)
    print("Полная демонстрация завершена!")
    print("=" * 80)


if __name__ == "__main__":
    main()
