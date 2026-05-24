"""
Интеллектуальный документный ассистент с совместной работой нескольких агентов

Используются два SimpleAgent с разделением обязанностей：
- Agent1：эксперт по поиску на GitHub
- Agent2：эксперт по генерации документов
"""
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv(dotenv_path="../HelloAgents/.env")

print("="*70)
print("Интеллектуальный документный ассистент с совместной работой нескольких агентов")
print("="*70)

# ============================================================
# Agent 1: эксперт по поиску на GitHub
# ============================================================
print("\n[Шаг 1] Создаём эксперта по поиску на GitHub...")

github_searcher = SimpleAgent(
    name="Эксперт по поиску на GitHub",
    llm=HelloAgentsLLM(),
    system_prompt="""Ты эксперт по поиску на GitHub.
Твоя задача — искать репозитории на GitHub и возвращать результаты.
Возвращай чёткие, структурированные результаты поиска, включая：
- Название репозитория
- Краткое описание

Будь лаконичен, не добавляй лишних пояснений."""
)

# Добавляем инструмент GitHub
github_tool = MCPTool(
    name="gh",
    server_command=["npx", "-y", "@modelcontextprotocol/server-github"]
)
github_searcher.add_tool(github_tool)

# ============================================================
# Agent 2: эксперт по генерации документов
# ============================================================
print("\n[Шаг 2] Создаём эксперта по генерации документов...")

document_writer = SimpleAgent(
    name="Эксперт по генерации документов",
    llm=HelloAgentsLLM(),
    system_prompt="""Ты эксперт по генерации документов.
Твоя задача — создавать структурированные Markdown-отчёты на основе предоставленной информации.

Отчёт должен включать：
- Заголовок
- Введение
- Основное содержимое（по пунктам, включая название проекта, описание и т.д.）
- Заключение

Выводи полный отчёт в формате Markdown напрямую, без сохранения через инструменты."""
)

# Добавляем инструмент файловой системы
fs_tool = MCPTool(
    name="fs",
    server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]
)
document_writer.add_tool(fs_tool)

# ============================================================
# Выполнение задачи
# ============================================================
print("\n" + "="*70)
print("Начинаем выполнение задачи...")
print("="*70)

try:
    # Шаг 1：поиск на GitHub
    print("\n[Шаг 3] Agent1 выполняет поиск на GitHub...")
    search_task = "Найди репозитории GitHub по теме 'AI agent', верни 5 наиболее релевантных результатов"

    search_results = github_searcher.run(search_task)

    print("\nРезультаты поиска:")
    print("-" * 70)
    print(search_results)
    print("-" * 70)

    # Шаг 2：генерация отчёта
    print("\n[Шаг 4] Agent2 генерирует отчёт...")
    report_task = f"""
На основе следующих результатов поиска GitHub сгенерируй исследовательский отчёт в формате Markdown：

{search_results}

Требования к отчёту：
1. Заголовок：# Исследовательский отчёт по фреймворкам AI Agent
2. Введение：опиши, что это исследование проектов AI Agent на GitHub
3. Основные выводы：перечисли найденные проекты и их особенности（включая название, описание и т.д.）
4. Заключение：подведи итог, выдели общие черты этих проектов

Выводи полный отчёт в формате Markdown напрямую.
"""

    report_content = document_writer.run(report_task)

    print("\nСодержимое отчёта:")
    print("=" * 70)
    print(report_content)
    print("=" * 70)

    # Шаг 3：сохранение отчёта
    print("\n[Шаг 5] Сохраняем отчёт в файл...")
    import os
    try:
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("Отчёт сохранён в report.md")

        # Проверяем файл
        file_size = os.path.getsize("report.md")
        print(f"Размер файла: {file_size} байт")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")

    print("\n" + "="*70)
    print("Задача выполнена！")
    print("="*70)

except Exception as e:
    print(f"\nОшибка: {e}")
    import traceback
    traceback.print_exc()
