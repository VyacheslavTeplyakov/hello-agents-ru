"""
Шаг 2: Только оценка уже сгенерированных задач AIME

Запуск:
python data_generation/step2_evaluate_only.py <generated_data_path>

Параметры:
- generated_data_path: путь к файлу с данными

Примечание:
- В качестве референса используются реальные задачи AIME 2025 года
- Источник датасета: math-ai/aime25 (формат JSONL)

Пример:
python data_generation/step2_evaluate_only.py data_generation/generated_data/aime_generated_20251011_042741.json
"""

import json
import os
import sys
from datetime import datetime
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import LLMJudgeTool, WinRateTool


def run_evaluation(generated_data_path: str):
    """
    Запуск цикла оценки

    Args:
        generated_data_path: путь к файлу с данными
    """
    print("\n" + "="*80)
    print("🎯 Шаг 2: Оценка уже сгенерированных задач AIME")
    print("="*80)
    print(f"\nКонфигурация:")
    print(f"  - Данные: {generated_data_path}")
    print(f"  - Референс: реальные задачи AIME 2025")

    # Проверяем, существует ли файл
    if not os.path.exists(generated_data_path):
        print(f"\n❌ Ошибка: файл не найден: {generated_data_path}")
        return

    # Загружаем данные, чтобы узнать количество задач
    with open(generated_data_path, 'r', encoding='utf-8') as f:
        generated_data = json.load(f)
    num_problems = len(generated_data)
    print(f"  - Количество задач: {num_problems}")

    # Создаём директорию для результатов оценки
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evaluation_dir = f"data_generation/evaluation_results/{timestamp}"
    os.makedirs(evaluation_dir, exist_ok=True)
    os.makedirs(os.path.join(evaluation_dir, "llm_judge"), exist_ok=True)
    os.makedirs(os.path.join(evaluation_dir, "win_rate"), exist_ok=True)

    # Создаём LLM
    llm = HelloAgentsLLM()

    # # ========== Оценка LLM Judge ==========
    print(f"\n🎯 Шаг 2.1: Оценка LLM Judge (vs AIME 2025)")

    llm_judge_result = None
    try:
        llm_judge_tool = LLMJudgeTool(llm=llm)

        llm_judge_result_json = llm_judge_tool.run({
            "generated_data_path": generated_data_path,
            "reference_year": 2025,
            "max_samples": num_problems,
            "output_dir": os.path.join(evaluation_dir, "llm_judge"),
            "judge_model": "gpt-4o"
        })

        llm_judge_result = json.loads(llm_judge_result_json)
        print(f"\n✅ Оценка LLM Judge завершена!")
        print(f"   Средний итоговый балл: {llm_judge_result['metrics']['average_total_score']:.2f}/5.0")
        print(f"   Доля прошедших: {llm_judge_result['metrics']['pass_rate']:.2%}")
    except Exception as e:
        print(f"\n❌ Оценка LLM Judge не удалась: {e}")
        import traceback
        traceback.print_exc()

    # ========== Оценка Win Rate ==========
    print(f"\n🏆 Шаг 2.2: Оценка Win Rate (vs AIME 2025)")

    win_rate_result = None
    try:
        win_rate_tool = WinRateTool(llm=llm)

        win_rate_result_json = win_rate_tool.run({
            "generated_data_path": generated_data_path,
            "reference_year": 2025,
            "num_comparisons": min(num_problems, 20),  # не более 20 сравнений
            "output_dir": os.path.join(evaluation_dir, "win_rate"),
            "judge_model": "gpt-4o"
        })

        win_rate_result = json.loads(win_rate_result_json)
        print(f"\n✅ Оценка Win Rate завершена!")
        print(f"   Win Rate: {win_rate_result['metrics']['win_rate']:.2%}")
    except Exception as e:
        print(f"\n❌ Оценка Win Rate не удалась: {e}")
        import traceback
        traceback.print_exc()

    # ========== Формирование сводного отчёта ==========
    comprehensive_report_path = None
    if llm_judge_result or win_rate_result:
        print("\n" + "="*80)
        print("📊 Шаг 2.3: Формирование сводного отчёта")
        print("="*80)

        comprehensive_report_path = os.path.join(evaluation_dir, "comprehensive_report.md")

        # Формируем сводный отчёт
        report = generate_comprehensive_report(
            generated_data_path,
            llm_judge_result,
            win_rate_result
        )

        with open(comprehensive_report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Сводный отчёт сохранён: {comprehensive_report_path}")

    # ========== Завершение ==========
    print("\n" + "="*80)
    print("🎉 Цикл оценки завершён!")
    print("="*80)
    print(f"\n📁 Выходные файлы:")
    print(f"   - Директория результатов: {evaluation_dir}")

    if llm_judge_result:
        print(f"   - Отчёт LLM Judge: {llm_judge_result.get('report_file', 'N/A')}")
    if win_rate_result:
        print(f"   - Отчёт Win Rate: {win_rate_result.get('report_file', 'N/A')}")

    if comprehensive_report_path:
        print(f"   - Сводный отчёт: {comprehensive_report_path}")

    print(f"\n💡 Следующие шаги:")
    if comprehensive_report_path:
        print(f"   1. Просмотрите сводный отчёт: {comprehensive_report_path}")
    print(f"   2. Запустите ручную верификацию: python data_generation/human_verification_ui.py {generated_data_path}")


def generate_comprehensive_report(
    generated_data_path: str,
    llm_judge_result: dict,
    win_rate_result: dict
) -> str:
    """Формирование сводного отчёта по оценке"""

    # Загружаем сгенерированные данные
    with open(generated_data_path, 'r', encoding='utf-8') as f:
        generated_data = json.load(f)

    report = f"""# Сводный отчёт по генерации и оценке данных AIME

## 1. Основная информация

- **Время генерации**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Количество сгенерированных задач**: {len(generated_data)}
- **Референсный год AIME**: 2025
- **Путь к данным**: {generated_data_path}

## 2. Статистика генерации данных

### Распределение по темам

"""

    # Считаем распределение по темам
    topic_counts = {}
    for item in generated_data:
        topic = item.get('topic', 'Unknown')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    report += "| Тема | Количество | Доля |\n"
    report += "|------|------------|------|\n"
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(generated_data) * 100
        report += f"| {topic} | {count} | {percentage:.1f}% |\n"

    # Результаты LLM Judge
    if llm_judge_result:
        report += "\n## 3. Результаты оценки LLM Judge\n\n"
        report += f"""**Общий балл**:
- Средний итоговый балл: {llm_judge_result['metrics']['average_total_score']:.2f}/5.0
- Доля прошедших: {llm_judge_result['metrics']['pass_rate']:.2%}
- Доля отличных: {llm_judge_result['metrics']['excellent_rate']:.2%}

**Баллы по измерениям**:

| Измерение | Средний балл |
|-----------|-------------|
| Корректность | {llm_judge_result['metrics']['dimension_averages']['correctness']:.2f}/5.0 |
| Чёткость | {llm_judge_result['metrics']['dimension_averages']['clarity']:.2f}/5.0 |
| Соответствие сложности | {llm_judge_result['metrics']['dimension_averages']['difficulty_match']:.2f}/5.0 |
| Полнота | {llm_judge_result['metrics']['dimension_averages']['completeness']:.2f}/5.0 |

"""

    # Результаты Win Rate
    if win_rate_result:
        report += "\n## 4. Результаты оценки Win Rate\n\n"
        report += f"""**Статистика побед**:
- Win Rate: {win_rate_result['metrics']['win_rate']:.2%}
- Loss Rate: {win_rate_result['metrics']['loss_rate']:.2%}
- Tie Rate: {win_rate_result['metrics']['tie_rate']:.2%}

**Количество сравнений**:
- Всего сравнений: {win_rate_result['metrics']['total_comparisons']}
- Побед: {win_rate_result['metrics']['wins']}
- Поражений: {win_rate_result['metrics']['losses']}
- Ничьих: {win_rate_result['metrics']['ties']}

"""

    # Общий вывод
    report += "\n## 5. Общий вывод\n\n"

    if llm_judge_result and win_rate_result:
        overall_avg_score = llm_judge_result['metrics']['average_total_score']
        overall_win_rate = win_rate_result['metrics']['win_rate']

        if overall_avg_score >= 4.5 and overall_win_rate >= 0.48:
            report += "✅ **Вывод**: качество сгенерированных данных **отличное** — соответствует или превосходит уровень реальных задач AIME.\n"
        elif overall_avg_score >= 4.0 and overall_win_rate >= 0.45:
            report += "✅ **Вывод**: качество сгенерированных данных **хорошее** — близко к уровню реальных задач AIME.\n"
        else:
            report += "⚠️ **Вывод**: качество сгенерированных данных **требует улучшения** — есть отставание от реальных задач AIME.\n"

        report += f"\n**Общие показатели**:\n"
        report += f"- Балл LLM Judge: {overall_avg_score:.2f}/5.0\n"
        report += f"- Win Rate: {overall_win_rate:.2%}\n"

    # Рекомендации по улучшению
    report += "\n## 6. Рекомендации по улучшению\n\n"

    if llm_judge_result:
        avg_score = llm_judge_result['metrics']['average_total_score']
        if avg_score >= 4.5:
            report += "- ✅ Продолжайте использовать текущую стратегию генерации\n"
            report += "- ✅ Можно рассмотреть увеличение объёма генерации\n"
        elif avg_score >= 4.0:
            report += "- 🔄 Оптимизируйте промпты для генерации задач\n"
            report += "- 🔄 Добавьте шаг фильтрации по качеству\n"
        else:
            report += "- ⚠️ Необходимо переработать промпты генерации\n"
            report += "- ⚠️ Рассмотрите использование более мощной генерирующей модели\n"
            report += "- ⚠️ Добавьте этап ручной проверки\n"

    # Следующие шаги
    report += "\n## 7. Следующие шаги\n\n"
    report += "1. **Ручная верификация**: запустите интерфейс ручной проверки для аудита сгенерированных задач\n"
    report += f"   ```bash\n   python data_generation/human_verification_ui.py {generated_data_path}\n   ```\n\n"
    report += "2. **Отбор по качеству**: отберите задачи с высоким качеством на основе результатов оценки\n\n"
    report += "3. **Итерационная оптимизация**: улучшите стратегию генерации на основе обратной связи\n"

    report += f"\n---\n\n*Отчёт сформирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    return report


def main():
    if len(sys.argv) < 2:
        print("Использование: python step2_evaluate_only.py <generated_data_path>")
        print("\nПримечание:")
        print("  - В качестве референса используются реальные задачи AIME 2025 года")
        print("  - Источник датасета: math-ai/aime25 (формат JSONL)")
        print("  - Требуется установка: pip install pandas pyarrow datasets")
        print("\nПример:")
        print("python step2_evaluate_only.py data_generation/generated_data/aime_generated_20251011_042741.json")
        sys.exit(1)

    generated_data_path = sys.argv[1]

    run_evaluation(generated_data_path)


if __name__ == "__main__":
    main()
