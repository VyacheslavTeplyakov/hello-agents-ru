"""
Глава 12, пример 6: Лучшие практики оценки GAIA

Соответствует документации: 12.3.9 Лучшие практики оценки GAIA

Этот пример демонстрирует лучшие практики оценки GAIA, включая:
1. Поуровневую оценку
2. Быстрое тестирование на малой выборке
3. Интерпретацию результатов
"""

import os
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import GAIAEvaluationTool

# Официальный системный промпт GAIA
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""

# Создаём агента
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="TestAgent",
    llm=llm,
    system_prompt=GAIA_SYSTEM_PROMPT
)

# Создаём инструмент оценки
gaia_tool = GAIAEvaluationTool()

# ============================================================
# Лучшая практика 1: Поуровневая оценка
# ============================================================
print("="*60)
print("Лучшая практика 1: Поуровневая оценка")
print("="*60)

# Шаг 1: Оцениваем Level 1 (лёгкие задачи)
print("\nШаг 1: Оцениваем Level 1 (лёгкие задачи)")
results_l1 = gaia_tool.run(agent, level=1, max_samples=10)
print(f"Level 1 точное совпадение: {results_l1['exact_match_rate']:.2%}")

# Шаг 2: Если Level 1 хорошо, оцениваем Level 2
if results_l1['exact_match_rate'] > 0.6:
    print("\nШаг 2: Оцениваем Level 2 (средние задачи)")
    results_l2 = gaia_tool.run(agent, level=2, max_samples=10)
    print(f"Level 2 точное совпадение: {results_l2['exact_match_rate']:.2%}")

    # Шаг 3: Если Level 2 хорошо, оцениваем Level 3
    if results_l2['exact_match_rate'] > 0.4:
        print("\nШаг 3: Оцениваем Level 3 (сложные задачи)")
        results_l3 = gaia_tool.run(agent, level=3, max_samples=10)
        print(f"Level 3 точное совпадение: {results_l3['exact_match_rate']:.2%}")
    else:
        print("\nLevel 2 слабый, рекомендуется сначала улучшить агента перед оценкой Level 3")
else:
    print("\nLevel 1 слабый, рекомендуется сначала улучшить агента перед оценкой более высоких уровней")

# ============================================================
# Лучшая практика 2: Быстрое тестирование на малой выборке
# ============================================================
print("\n" + "="*60)
print("Лучшая практика 2: Быстрое тестирование на малой выборке")
print("="*60)

# Быстрый тест (по 2 примера на каждый уровень)
for level in [1, 2, 3]:
    print(f"\nБыстрый тест Level {level}:")
    results = gaia_tool.run(agent, level=level, max_samples=2)
    print(f"  Точное совпадение: {results['exact_match_rate']:.2%}")

# ============================================================
# Лучшая практика 3: Интерпретация результатов
# ============================================================
print("\n" + "="*60)
print("Лучшая практика 3: Интерпретация результатов")
print("="*60)

def interpret_results(level, exact_match_rate):
    """Интерпретирует результаты оценки"""
    print(f"\nLevel {level} — интерпретация результатов:")
    print(f"Точное совпадение: {exact_match_rate:.2%}")

    if level == 1:
        if exact_match_rate >= 0.6:
            print("Отлично — базовые возможности на высоком уровне")
        elif exact_match_rate >= 0.4:
            print("Хорошо — базовые возможности приемлемы")
        else:
            print("Слабо — необходимо улучшение")
            print("Рекомендации:")
            print("  - Проверьте, содержит ли системный промпт требования к формату ответа GAIA")
            print("  - Проверьте корректность логики извлечения ответа")
            print("  - Проверьте, достаточно ли мощная используемая LLM-модель")

    elif level == 2:
        if exact_match_rate >= 0.4:
            print("Отлично — сильные возможности для задач среднего уровня")
        elif exact_match_rate >= 0.2:
            print("Хорошо — возможности для задач среднего уровня приемлемы")
        else:
            print("Слабо — необходимо улучшение")
            print("Рекомендации:")
            print("  - Улучшите возможности многошагового рассуждения")
            print("  - Расширьте возможности использования инструментов")
            print("  - Оптимизируйте построение цепочек рассуждений")

    elif level == 3:
        if exact_match_rate >= 0.2:
            print("Отлично — сильные возможности для сложных задач")
        elif exact_match_rate >= 0.1:
            print("Хорошо — возможности для сложных задач приемлемы")
        else:
            print("Слабо — необходимо улучшение")
            print("Рекомендации:")
            print("  - Улучшите возможности сложного рассуждения")
            print("  - Расширьте возможности работы с длинным контекстом")
            print("  - Оптимизируйте комбинированное использование цепочки инструментов")

# Интерпретируем результаты
if 'results_l1' in locals():
    interpret_results(1, results_l1['exact_match_rate'])
if 'results_l2' in locals():
    interpret_results(2, results_l2['exact_match_rate'])
if 'results_l3' in locals():
    interpret_results(3, results_l3['exact_match_rate'])

# ============================================================
# Анализ нарастания сложности
# ============================================================
print("\n" + "="*60)
print("Анализ нарастания сложности")
print("="*60)

if 'results_l1' in locals() and 'results_l2' in locals():
    if results_l1['exact_match_rate'] > results_l2['exact_match_rate']:
        print("Нормальное нарастание: Level 1 > Level 2")
    else:
        print("Аномалия: Level 2 >= Level 1 (возможно смещение в данных или особенности агента)")

if 'results_l2' in locals() and 'results_l3' in locals():
    if results_l2['exact_match_rate'] > results_l3['exact_match_rate']:
        print("Нормальное нарастание: Level 2 > Level 3")
    else:
        print("Аномалия: Level 3 >= Level 2 (возможно смещение в данных или особенности агента)")
