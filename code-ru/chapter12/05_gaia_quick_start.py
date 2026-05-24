"""
Глава 12, пример 5: Быстрый старт с GAIA

Соответствует документации: 12.3.5 Реализация оценки GAIA в HelloAgents — способ 1

Это простейший способ оценки GAIA: одна строка кода выполняет оценку.

Важные примечания:
1. GAIA — ограниченный набор данных, сначала нужно запросить доступ на HuggingFace
2. Необходимо задать переменную окружения HF_TOKEN
3. Обязательно использовать официальный системный промпт GAIA
"""

import os
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import GAIAEvaluationTool

# Официальный системный промпт GAIA (обязательно использовать)
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""

# 1. Задаём токен HuggingFace (если ещё не задан)
# os.environ["HF_TOKEN"] = "your_huggingface_token_here"

# 2. Создаём агента (обязательно с официальным системным промптом GAIA)
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="TestAgent",
    llm=llm,
    system_prompt=GAIA_SYSTEM_PROMPT  # обязательно использовать официальный промпт
)

# 3. Создаём инструмент оценки GAIA
gaia_tool = GAIAEvaluationTool()

# 4. Запускаем оценку
results = gaia_tool.run(
    agent=agent,
    level=1,              # уровень оценки (1=лёгкий, 2=средний, 3=сложный)
    max_samples=2,        # количество примеров (0 = все)
    export_results=True,  # экспортировать результаты в официальный формат GAIA
    generate_report=True  # генерировать подробный отчёт
)

# 5. Смотрим результаты
print(f"\nРезультаты оценки:")
print(f"Точное совпадение: {results['exact_match_rate']:.2%}")
print(f"Частичное совпадение: {results['partial_match_rate']:.2%}")
print(f"Верных ответов: {results['correct_samples']}/{results['total_samples']}")

# Пример вывода при запуске:
# ============================================================
# Оценка GAIA в один клик
# ============================================================
#
# Конфигурация:
#    Агент: TestAgent
#    Уровень: Level 1
#    Примеров: 2
#
# Набор данных GAIA загружен
#    Источник: gaia-benchmark/GAIA
#    Раздел: validation
#    Уровень: 1
#    Примеров: 2
#
# Прогресс оценки: 100%|██████████| 2/2 [00:10<00:00,  5.23 с/пример]
#
# Оценка завершена
#    Всего примеров: 2
#    Верных примеров: 2
#    Точное совпадение: 100.00%
#    Частичное совпадение: 100.00%
#
# Результаты экспортированы в ./evaluation_results/gaia_submission.json
# Отчёт сохранён в ./evaluation_results/gaia_report.md
#
# Результаты оценки:
# Точное совпадение: 100.00%
# Частичное совпадение: 100.00%
# Верных ответов: 2/2
