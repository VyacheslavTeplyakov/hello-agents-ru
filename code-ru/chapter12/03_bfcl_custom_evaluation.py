"""
Глава 12, пример 3: Кастомная оценка BFCL

Соответствует документации: 12.2.5 Реализация оценки BFCL в HelloAgents — способ 3

Этот пример показывает, как использовать низкоуровневые компоненты
для создания кастомного процесса оценки.
Подходит для сценариев, требующих настройки процесса оценки.
"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.evaluation import BFCLDataset, BFCLEvaluator

# 1. Создаём агента
llm = HelloAgentsLLM()
agent = SimpleAgent(name="TestAgent", llm=llm)

# 2. Загружаем набор данных
dataset = BFCLDataset(
    bfcl_data_dir="./temp_gorilla/berkeley-function-call-leaderboard/bfcl_eval/data",
    category="simple_python"
)
data = dataset.load()

print(f"Загружено {len(data)} тестовых примеров")

# 3. Создаём оценщик
evaluator = BFCLEvaluator(
    dataset=dataset,
    category="simple_python"
)

# 4. Запускаем оценку
results = evaluator.evaluate(
    agent=agent,
    max_samples=5  # оцениваем только 5 примеров
)

# 5. Смотрим подробные результаты
print(f"\nРезультаты оценки:")
print(f"Всего примеров: {results['total_samples']}")
print(f"Верных примеров: {results['correct_samples']}")
print(f"Точность: {results['overall_accuracy']:.2%}")

# 6. Смотрим детали по каждому примеру
print(f"\nДетальные результаты:")
for detail in results['detailed_results']:
    print(f"Пример {detail['sample_id']}:")
    print(f"  Вопрос: {detail['question'][:50]}...")
    print(f"  Предсказание: {detail['predicted']}")
    print(f"  Правильный ответ: {detail['expected']}")
    print(f"  Результат: {'Верно' if detail['success'] else 'Неверно'}")
    print()

# 7. Экспортируем результаты
evaluator.export_results(
    results,
    output_file="./evaluation_results/bfcl_custom_result.json"
)

print("Результаты экспортированы в ./evaluation_results/bfcl_custom_result.json")
