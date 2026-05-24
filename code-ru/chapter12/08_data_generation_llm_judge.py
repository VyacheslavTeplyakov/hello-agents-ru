"""
Глава 12, пример 8: Оценка с помощью LLM Judge

Соответствует документации: 12.4.3 Оценка LLM Judge

Этот пример показывает, как использовать LLM Judge для оценки
качества сгенерированных задач AIME.

LLM Judge оценивает качество задач по 4 измерениям:
1. Правильность (Correctness): правильны ли задача и ответ
2. Ясность (Clarity): насколько чётко сформулирована задача
3. Соответствие сложности (Difficulty Match): соответствует ли сложность уровню AIME
4. Полнота (Completeness): полна ли задача
"""

import sys
import os
import json

# Добавляем путь к HelloAgents
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "HelloAgents"))

from hello_agents import HelloAgentsLLM
from hello_agents.evaluation import LLMJudge

# 1. Готовим сгенерированные задачи
generated_problems = [
    {
        "problem_id": "generated_001",
        "problem": "Find the number of positive integers $n$ such that $n^2 + 19n + 92$ is a perfect square.",
        "answer": "4",
        "solution": "Let $n^2 + 19n + 92 = m^2$ for some positive integer $m$..."
    },
    {
        "problem_id": "generated_002",
        "problem": "In triangle $ABC$, $AB = 13$, $BC = 14$, and $CA = 15$. Find the area of the triangle.",
        "answer": "84",
        "solution": "Using Heron's formula, $s = (13+14+15)/2 = 21$..."
    }
]

# 2. Создаём оценщик LLM Judge
llm = HelloAgentsLLM(model_name="gpt-4o")
judge = LLMJudge(llm=llm)

# 3. Оцениваем каждую задачу
print("="*60)
print("Оценка LLM Judge")
print("="*60)

all_scores = []

for i, problem in enumerate(generated_problems, 1):
    print(f"\nОценка задачи {i}/{len(generated_problems)}")
    print(f"ID задачи: {problem['problem_id']}")

    # Оцениваем одну задачу
    result = judge.evaluate_single(problem)

    # Отображаем результаты оценки
    print(f"\nРезультат оценки:")
    print(f"  Правильность: {result['correctness']}/5")
    print(f"  Ясность: {result['clarity']}/5")
    print(f"  Соответствие сложности: {result['difficulty_match']}/5")
    print(f"  Полнота: {result['completeness']}/5")
    print(f"  Средний балл: {result['average_score']:.2f}/5")
    print(f"\nОтзыв:")
    print(f"  {result['feedback']}")

    all_scores.append(result)

# 4. Вычисляем общую статистику
print("\n" + "="*60)
print("Общая статистика")
print("="*60)

avg_correctness = sum(s['correctness'] for s in all_scores) / len(all_scores)
avg_clarity = sum(s['clarity'] for s in all_scores) / len(all_scores)
avg_difficulty = sum(s['difficulty_match'] for s in all_scores) / len(all_scores)
avg_completeness = sum(s['completeness'] for s in all_scores) / len(all_scores)
avg_overall = sum(s['average_score'] for s in all_scores) / len(all_scores)

print(f"\nСредние баллы:")
print(f"  Правильность: {avg_correctness:.2f}/5")
print(f"  Ясность: {avg_clarity:.2f}/5")
print(f"  Соответствие сложности: {avg_difficulty:.2f}/5")
print(f"  Полнота: {avg_completeness:.2f}/5")
print(f"  Общий средний: {avg_overall:.2f}/5")

# 5. Оценка качества
print(f"\nОценка качества:")
if avg_overall >= 4.0:
    print("Отлично — качество задач высокое, можно использовать сразу")
elif avg_overall >= 3.0:
    print("Хорошо — качество задач приемлемо, рекомендуется ручная проверка")
elif avg_overall >= 2.0:
    print("Удовлетворительно — качество задач среднее, требует существенных улучшений")
else:
    print("Плохо — качество задач низкое, необходима повторная генерация")

# 6. Сохраняем результаты оценки
output_file = "./evaluation_results/llm_judge_results.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'problems': generated_problems,
        'scores': all_scores,
        'statistics': {
            'avg_correctness': avg_correctness,
            'avg_clarity': avg_clarity,
            'avg_difficulty': avg_difficulty,
            'avg_completeness': avg_completeness,
            'avg_overall': avg_overall
        }
    }, f, indent=2, ensure_ascii=False)

print(f"\nРезультаты оценки сохранены в {output_file}")

# Пример вывода при запуске:
# ============================================================
# Оценка LLM Judge
# ============================================================
#
# Оценка задачи 1/2
# ID задачи: generated_001
#
# Результат оценки:
#   Правильность: 5/5
#   Ясность: 4/5
#   Соответствие сложности: 5/5
#   Полнота: 5/5
#   Средний балл: 4.75/5
#
# Отзыв:
#   This is an excellent AIME-level problem. The problem is well-posed,
#   the solution is correct, and the difficulty is appropriate.
#
# Оценка задачи 2/2
# ID задачи: generated_002
#
# Результат оценки:
#   Правильность: 5/5
#   Ясность: 5/5
#   Соответствие сложности: 3/5
#   Полнота: 5/5
#   Средний балл: 4.50/5
#
# Отзыв:
#   The problem is correct and clear, but the difficulty is slightly
#   below AIME level. Consider adding more complexity.
#
# ============================================================
# Общая статистика
# ============================================================
#
# Средние баллы:
#   Правильность: 5.00/5
#   Ясность: 4.50/5
#   Соответствие сложности: 4.00/5
#   Полнота: 5.00/5
#   Общий средний: 4.62/5
#
# Оценка качества:
# Отлично — качество задач высокое, можно использовать сразу
#
# Результаты оценки сохранены в ./evaluation_results/llm_judge_results.json
