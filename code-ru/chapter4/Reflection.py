from typing import List, Dict, Any, Optional
# Предполагается, что llm_client.py определен в той же папке
from llm_client import HelloAgentsLLM

# --- Модуль 1: Модуль памяти ---

class Memory:
    """
    Простой модуль краткосрочной памяти для хранения действий агента и траектории рефлексии.
    """
    def __init__(self):
        # Инициализируем пустой список для хранения записей
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_type: str, content: str):
        """
        Добавляет новую запись в память.

        Параметры:
        - record_type (str): Тип записи ('execution' или 'reflection').
        - content (str): Конкретное содержимое записи (например, сгенерированный код или отзыв рефлексии).
        """
        self.records.append({"type": record_type, "content": content})
        print(f"📝 Память обновлена, добавлена запись типа '{record_type}'.")

    def get_trajectory(self) -> str:
        """
        Форматирует все записи памяти в связный текстовый сегмент для построения промптов.
        """
        trajectory_parts = []
        for record in self.records:
            if record['type'] == 'execution':
                trajectory_parts.append(f"--- Предыдущая попытка (код) ---\n{record['content']}")
            elif record['type'] == 'reflection':
                trajectory_parts.append(f"--- Отзыв рецензента ---\n{record['content']}")
        return "\n\n".join(trajectory_parts)

    def get_last_execution(self) -> Optional[str]:
        """
        Возвращает самый последний результат выполнения (например, последний сгенерированный код).
        Возвращает None, если записей о выполнении нет.
        """
        for record in reversed(self.records):
            if record['type'] == 'execution':
                return record['content']
        return None

# --- Модуль 2: Reflection-агент ---

# 1. Шаблон для первоначального написания кода
INITIAL_PROMPT_TEMPLATE = """
Вы — опытный Python-программист. Пожалуйста, напишите функцию на Python в соответствии со следующими требованиями.
Ваш код должен содержать полную сигнатуру функции, docstring и соответствовать стандартам кодирования PEP 8.

Требование: {task}

Пожалуйста, выводите только код напрямую, без каких-либо дополнительных объяснений.
"""

# 2. Шаблон для рефлексии (код-ревью)
REFLECT_PROMPT_TEMPLATE = """
Вы — чрезвычайно строгий эксперт по код-ревью и опытный инженер-алгоритмист, предъявляющий высочайшие требования к производительности кода.
Ваша задача — проанализировать следующий код на Python и сфокусироваться на поиске его основного узкого места с точки зрения **эффективности алгоритма**.

# Исходное задание:
{task}

# Код для проверки:
```python
{code}
```

Пожалуйста, проанализируйте временную сложность этого кода и подумайте, существует ли **алгоритмически более совершенное** решение для значительного повышения производительности.
Если такое решение есть, четко укажите на недостатки текущего алгоритма и предложите конкретные, выполнимые рекомендации по улучшению (например, использование метода решета вместо деления на потенциальные делители).
Только если код уже достиг оптимального уровня с точки зрения алгоритма, вы можете ответить "no improvement needed" (улучшение не требуется).

Пожалуйста, выводите свой отзыв напрямую, без каких-либо дополнительных объяснений.
"""

# 3. Шаблон для оптимизации кода на основе рефлексии
REFINE_PROMPT_TEMPLATE = """
Вы — опытный Python-программист. Вы оптимизируете свой код на основе отзыва эксперта по код-ревью.

# Исходное задание:
{task}

# Ваша предыдущая версия кода:
{last_code_attempt}

# Отзыв рецензента:
{feedback}

Пожалуйста, сгенерируйте новую оптимизированную версию кода на основе отзыва рецензента.
Ваш код должен содержать полную сигнатуру функции, docstring и соответствовать стандартам кодирования PEP 8.
Пожалуйста, выводите оптимизированный код напрямую, без каких-либо дополнительных объяснений.
"""

class ReflectionAgent:
    def __init__(self, llm_client: HelloAgentsLLM, max_iterations: int = 3):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations

    def run(self, task: str):
        print(f"\n--- Начало обработки задачи ---\nЗадача: {task}")

        # --- 1. Первоначальное выполнение ---
        print("\n--- Выполнение первоначальной попытки ---")
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)

        # --- 2. Цикл итераций: рефлексия и оптимизация ---
        for i in range(self.max_iterations):
            print(f"\n--- Итерация {i+1}/{self.max_iterations} ---")

            # а. Рефлексия (код-ревью)
            print("\n-> Выполнение рефлексии...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)

            # б. Проверка условия остановки
            if "no improvement needed" in feedback.lower() or "улучшение не требуется" in feedback.lower() or "无需改进" in feedback:
                print("\n✅ Рефлексия считает, что код не требует улучшений, задача выполнена.")
                break

            # в. Оптимизация (исправление по фидбеку)
            print("\n-> Выполнение оптимизации...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)
        
        final_code = self.memory.get_last_execution()
        print(f"\n--- Задача выполнена ---\nИтоговый сгенерированный код:\n{final_code}")
        return final_code

    def _get_llm_response(self, prompt: str) -> str:
        """Вспомогательный метод для вызова LLM и получения полного потокового ответа."""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""
        return response_text

if __name__ == '__main__':
    # 1. Инициализация LLM-клиента
    try:
        llm_client = HelloAgentsLLM()
    except Exception as e:
        print(f"Ошибка при инициализации LLM-клиента: {e}")
        exit()

    # 2. Инициализация Reflection-агента (максимум 2 итерации)
    agent = ReflectionAgent(llm_client, max_iterations=2)

    # 3. Запуск агента для решения задачи
    task = "Напишите функцию на Python для поиска всех простых чисел (prime numbers) от 1 до n."
    agent.run(task)
