import os
import ast
from llm_client import HelloAgentsLLM
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env, обрабатывая возможные исключения
try:
    load_dotenv()
except FileNotFoundError:
    print("Предупреждение: файл .env не найден, будут использоваться системные переменные окружения.")
except Exception as e:
    print(f"Предупреждение: ошибка при загрузке файла .env: {e}")

# --- 1. Определение LLM-клиента ---
# Предполагается, что в llm_client.py определен класс HelloAgentsLLM

# --- 2. Определение Планировщика (Planner) ---
PLANNER_PROMPT_TEMPLATE = """
Вы — первоклассный эксперт по планированию ИИ. Ваша задача — разбить сложный вопрос пользователя на план действий, состоящий из нескольких простых шагов.
Убедитесь, что каждый шаг плана является независимой выполнимой подзадачей и строго следует логическому порядку.
Ваш вывод должен быть в виде Python-списка, где каждый элемент — строка с описанием подзадачи.

Вопрос: {question}

Пожалуйста, строго придерживайтесь следующего формата вывода (использование префиксов и суффиксов ```python и ``` обязательно):
```python
["Шаг 1", "Шаг 2", "Шаг 3", ...]
```
"""

class Planner:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def plan(self, question: str) -> list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        
        print("--- Генерация плана ---")
        response_text = self.llm_client.think(messages=messages) or ""
        print(f"✅ План сгенерирован:\n{response_text}")
        
        try:
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ Ошибка при синтаксическом анализе плана: {e}")
            print(f"Исходный ответ: {response_text}")
            return []
        except Exception as e:
            print(f"❌ Неизвестная ошибка при синтаксическом анализе плана: {e}")
            return []

# --- 3. Определение Исполнителя (Executor) ---
EXECUTOR_PROMPT_TEMPLATE = """
Вы — первоклассный эксперт по выполнению задач ИИ. Ваша задача — строго следовать заданному плану и решать задачу шаг за шагом.
Вы получите исходный вопрос, полный план, а также выполненные к настоящему моменту шаги и их результаты.
Пожалуйста, сфокусируйтесь на решении «Текущего шага» и выведите только финальный ответ для этого шага, без каких-либо дополнительных объяснений или диалогов.

# Исходный вопрос:
{question}

# Полный план:
{plan}

# История выполненных шагов и их результаты:
{history}

# Текущий шаг:
{current_step}

Пожалуйста, выведите ответ только на «Текущий шаг»:
"""

class Executor:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def execute(self, question: str, plan: list[str]) -> str:
        history = ""
        final_answer = ""
        
        print("\n--- Выполнение плана ---")
        for i, step in enumerate(plan, 1):
            print(f"\n-> Выполняем шаг {i}/{len(plan)}: {step}")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question, plan=plan, history=history if history else "Нет", current_step=step
            )
            messages = [{"role": "user", "content": prompt}]
            
            response_text = self.llm_client.think(messages=messages) or ""
            
            history += f"Шаг {i}: {step}\nРезультат: {response_text}\n\n"
            final_answer = response_text
            print(f"✅ Шаг {i} завершен, результат: {final_answer}")
            
        return final_answer

# --- 4. Интеграция Агента (PlanAndSolveAgent) ---
class PlanAndSolveAgent:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        print(f"\n--- Начало обработки вопроса ---\nВопрос: {question}")
        plan = self.planner.plan(question)
        if not plan:
            print("\n--- Задача прервана --- \nНе удалось сгенерировать корректный план действий.")
            return
        final_answer = self.executor.execute(question, plan)
        print(f"\n--- Задача выполнена ---\nФинальный ответ: {final_answer}")

# --- 5. Точка входа в программу ---
if __name__ == '__main__':
    try:
        llm_client = HelloAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        question = "В фруктовом магазине в понедельник продали 15 яблок. Во вторник продали вдвое больше, чем в понедельник. В среду продали на 5 меньше, чем во вторник. Сколько яблок было продано за три дня в целом?"
        agent.run(question)
    except ValueError as e:
        print(e)
