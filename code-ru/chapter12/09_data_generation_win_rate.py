"""
Глава 12, пример 9: Оценка Win Rate

Соответствует документации: 12.4.4 Оценка Win Rate

Этот пример показывает, как использовать Win Rate для оценки
качества сгенерированных задач AIME.

Оценка Win Rate сравнивает сгенерированные задачи с реальными:
- Win Rate = 50%: качество генерации сопоставимо с реальными задачами (идеально)
- Win Rate > 50%: качество генерации выше реальных задач (возможна ошибка оценки)
- Win Rate < 50%: качество генерации ниже реальных задач (требует улучшения)
"""

import sys
import os
import json

# Добавляем путь к HelloAgents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "HelloAgents"))

from hello_agents import HelloAgentsLLM
from hello_agents.evaluation import WinRateEvaluator, AIDataset

# 1. Готовим сгенерированные задачи
generated_problems = [
    {
        "problem_id": "generated_001",
        "problem": "Find the number of positive integers $n$ such that $n^2 + 19n + 92$ is a perfect square.",
        "answer": "4"
    },
    {
        "problem_id": "generated_002",
        "problem": "In triangle $ABC$, $AB = 13$, $BC = 14$, and $CA = 15$. Find the area of the triangle.",
        "answer": "84"
    },
    {
        "problem_id": "generated_003",
        "problem": "How many positive integers less than 1000 are divisible by 7 but not by 11?",
        "answer": "129"
    }
]

# 2. Загружаем эталонный набор данных (реальные задачи AIME)
print("="*60)
print("Оценка Win Rate")
print("="*60)

print("\nЗагрузка эталонного набора данных...")
dataset = AIDataset()
reference_problems = dataset.load()
print(f"Загружено {len(reference_problems)} реальных задач AIME")

# 3. Создаём оценщик Win Rate
llm = HelloAgentsLLM(model_name="gpt-4o")
evaluator = WinRateEvaluator(
    llm=llm,
    reference_problems=reference_problems
)

# 4. Запускаем оценку Win Rate
print(f"\nНачало оценки Win Rate...")
print(f"  Сгенерированных задач: {len(generated_problems)}")
print(f"  Количество сравнений: 20")

results = evaluator.evaluate(
    generated_problems=generated_problems,
    num_comparisons=20  # выполнить 20 сравнений
)

# 5. Отображаем результаты оценки
print("\n" + "="*60)
print("Результаты оценки")
print("="*60)

print(f"\nWin Rate: {results['win_rate']:.2%}")
print(f"Tie Rate: {results['tie_rate']:.2%}")
print(f"Loss Rate: {results['loss_rate']:.2%}")

print(f"\nДетальная статистика:")
print(f"  Всего сравнений: {results['total_comparisons']}")
print(f"  Побед сгенерированных задач: {results['wins']}")
print(f"  Ничьих: {results['ties']}")
print(f"  Побед реальных задач: {results['losses']}")

# 6. Оценка качества
print(f"\nОценка качества:")
win_rate = results['win_rate']

if 0.45 <= win_rate <= 0.55:
    print("Отлично — качество генерации близко к уровню реальных задач AIME")
elif 0.35 <= win_rate < 0.45:
    print("Хорошо — качество генерации приемлемо, но немного уступает реальным задачам")
elif 0.25 <= win_rate < 0.35:
    print("Удовлетворительно — качество генерации среднее, требует улучшений")
else:
    print("Плохо — качество генерации низкое, требует существенных улучшений")

# 7. Просматриваем часть деталей сравнений
print("\n" + "="*60)
print("Детали сравнений (первые 5)")
print("="*60)

for i, comparison in enumerate(results['comparisons'][:5], 1):
    print(f"\nСравнение {i}:")
    print(f"  Сгенерированная задача: {comparison['generated_problem'][:60]}...")
    print(f"  Реальная задача: {comparison['reference_problem'][:60]}...")
    print(f"  Результат: {comparison['result']}")
    if 'reason' in comparison:
        print(f"  Обоснование: {comparison['reason'][:100]}...")

# 8. Сохраняем результаты оценки
output_file = "./evaluation_results/win_rate_results.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nРезультаты оценки сохранены в {output_file}")

# Пример вывода при запуске:
# ============================================================
# Оценка Win Rate
# ============================================================
#
# Загрузка эталонного набора данных...
# Загружено 963 реальных задачи AIME
#
# Начало оценки Win Rate...
#   Сгенерированных задач: 3
#   Количество сравнений: 20
#
# Оценка Win Rate: 100%|██████████| 20/20 [01:00<00:00,  3.01 с/сравн.]
#
# ============================================================
# Результаты оценки
# ============================================================
#
# Win Rate: 45.00%
# Tie Rate: 10.00%
# Loss Rate: 45.00%
#
# Детальная статистика:
#   Всего сравнений: 20
#   Побед сгенерированных задач: 9
#   Ничьих: 2
#   Побед реальных задач: 9
#
# Оценка качества:
# Отлично — качество генерации близко к уровню реальных задач AIME
#
# ============================================================
# Детали сравнений (первые 5)
# ============================================================
#
# Сравнение 1:
#   Сгенерированная задача: Find the number of positive integers $n$ such that $n^2 + 19...
#   Реальная задача: Let $N$ be the number of consecutive $0$'s at the right end...
#   Результат: generated
#   Обоснование: The generated problem has a clearer problem statement and a mo...
#
# Сравнение 2:
#   Сгенерированная задача: In triangle $ABC$, $AB = 13$, $BC = 14$, and $CA = 15$. F...
#   Реальная задача: Find the number of ordered pairs $(m,n)$ of positive integers...
#   Результат: reference
#   Обоснование: The reference problem is more challenging and requires deeper...
#
# ...
#
# Результаты оценки сохранены в ./evaluation_results/win_rate_results.json
