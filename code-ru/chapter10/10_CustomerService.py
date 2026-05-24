"""
10.3.4 Использование инструмента A2A в агенте
(2) Практический пример：интеллектуальная система обслуживания клиентов
"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import A2ATool
from hello_agents.protocols import A2AServer
import threading
import time
from dotenv import load_dotenv

load_dotenv()
llm = HelloAgentsLLM()

# 1. Создаём сервис агента — технического эксперта
tech_expert = A2AServer(
    name="tech_expert",
    description="Технический эксперт, отвечает на технические вопросы"
)

@tech_expert.skill("answer")
def answer_tech_question(text: str) -> str:
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text
    # В реальном приложении здесь вызывался бы LLM или база знаний
    return f"Технический ответ：по вопросу '{question}' рекомендуем обратиться к нашей технической документации..."

# 2. Создаём сервис агента — консультанта по продажам
sales_advisor = A2AServer(
    name="sales_advisor",
    description="Консультант по продажам, отвечает на вопросы о продажах"
)

@sales_advisor.skill("answer")
def answer_sales_question(text: str) -> str:
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text
    return f"Ответ по продажам：по вопросу '{question}' — у нас есть специальные предложения..."

# 3. Запускаем сервисы
threading.Thread(target=lambda: tech_expert.run(port=6000), daemon=True).start()
threading.Thread(target=lambda: sales_advisor.run(port=6001), daemon=True).start()
time.sleep(2)

# 4. Создаём агента-администратора（с SimpleAgent из HelloAgents）
receptionist = SimpleAgent(
    name="Администратор",
    llm=llm,
    system_prompt="""Ты администратор службы поддержки клиентов, в твои обязанности входит：
1. Анализировать тип вопроса клиента（технический или по продажам）
2. Перенаправлять вопрос соответствующему эксперту
3. Обобщить ответ эксперта и вернуть клиенту

Сохраняй вежливость и профессионализм."""
)

# Добавляем инструмент технического эксперта
tech_tool = A2ATool(
    agent_url="http://localhost:6000",
    name="tech_expert",
    description="Технический эксперт, отвечает на технические вопросы"
)
receptionist.add_tool(tech_tool)

# Добавляем инструмент консультанта по продажам
sales_tool = A2ATool(
    agent_url="http://localhost:6001",
    name="sales_advisor",
    description="Консультант по продажам, отвечает на вопросы о ценах и покупке"
)
receptionist.add_tool(sales_tool)

# 5. Обрабатываем запросы клиентов
def handle_customer_query(query):
    print(f"\nЗапрос клиента：{query}")
    print("=" * 50)
    response = receptionist.run(query)
    print(f"\nОтвет службы поддержки：{response}")
    print("=" * 50)

# Тестируем разные типы вопросов
if __name__ == "__main__":
    handle_customer_query("Как вызвать ваш API?")
    handle_customer_query("Сколько стоит корпоративная версия?")
    handle_customer_query("Как интегрировать в мой Python-проект?")
