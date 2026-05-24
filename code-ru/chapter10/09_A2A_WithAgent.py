"""
Пример интеграции протокола A2A и SimpleAgent из HelloAgents

Показывает, как интегрировать агента протокола A2A как инструмент в SimpleAgent
"""

from hello_agents.protocols import A2AServer, A2AClient
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import ToolRegistry, Tool, ToolParameter
import threading
import time
from typing import Dict, Any

# ============================================================
# 1. Создаём специализированные сервисы A2A Agent
# ============================================================

# Агент — технический эксперт
tech_expert = A2AServer(
    name="tech_expert",
    description="Технический эксперт, отвечает на технические вопросы",
    version="1.0.0"
)

@tech_expert.skill("answer")
def answer_tech_question(text: str) -> str:
    """Отвечает на технические вопросы"""
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text

    print(f"  [Технический эксперт] Отвечаю на вопрос: {question}")
    return f"Технический ответ：по вопросу '{question}' — профессиональный ответ на технический вопрос..."

# Агент — консультант по продажам
sales_advisor = A2AServer(
    name="sales_advisor",
    description="Консультант по продажам, отвечает на вопросы о продажах",
    version="1.0.0"
)

@sales_advisor.skill("answer")
def answer_sales_question(text: str) -> str:
    """Отвечает на вопросы о продажах"""
    import re
    match = re.search(r'answer\s+(.+)', text, re.IGNORECASE)
    question = match.group(1).strip() if match else text

    print(f"  [Консультант по продажам] Отвечаю на вопрос: {question}")
    return f"Ответ по продажам：по вопросу '{question}' — у нас есть специальные предложения..."

# ============================================================
# 2. Запускаем сервисы A2A Agent
# ============================================================

print("="*60)
print("Запускаем специализированные сервисы Agent")
print("="*60)

threading.Thread(target=lambda: tech_expert.run(port=6000), daemon=True).start()
threading.Thread(target=lambda: sales_advisor.run(port=6001), daemon=True).start()

print("Технический эксперт Agent запущен на http://localhost:6000")
print("Консультант по продажам Agent запущен на http://localhost:6001")

print("\nОжидаем запуска сервисов...")
time.sleep(3)

# ============================================================
# 3. Создаём инструменты A2A（оборачиваем A2A Agent как Tool）
# ============================================================

class A2ATool(Tool):
    """Оборачиваем A2A Agent как Tool для HelloAgents"""

    def __init__(self, name: str, description: str, agent_url: str, skill_name: str = "answer"):
        self.agent_url = agent_url
        self.skill_name = skill_name
        self.client = A2AClient(agent_url)
        self._name = name
        self._description = description
        self._parameters = [
            ToolParameter(
                name="question",
                type="string",
                description="Вопрос для отправки",
                required=True
            )
        ]

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def get_parameters(self) -> list[ToolParameter]:
        """Получаем параметры инструмента"""
        return self._parameters

    def run(self, **kwargs) -> str:
        """Выполняем инструмент"""
        question = kwargs.get('question', '')
        result = self.client.execute_skill(self.skill_name, f"answer {question}")
        if result.get('status') == 'success':
            return result.get('result', 'No response')
        else:
            return f"Error: {result.get('error', 'Unknown error')}"

# Создаём инструменты
tech_tool = A2ATool(
    name="tech_expert",
    description="Технический эксперт, отвечает на технические вопросы",
    agent_url="http://localhost:6000"
)

sales_tool = A2ATool(
    name="sales_advisor",
    description="Консультант по продажам, отвечает на вопросы о продажах",
    agent_url="http://localhost:6001"
)

# ============================================================
# 4. Создаём SimpleAgent（с инструментами A2A）
# ============================================================

print("\n" + "="*60)
print("Создаём SimpleAgent-администратора")
print("="*60)

# Инициализируем LLM
llm = HelloAgentsLLM()

# Создаём агента-администратора
receptionist = SimpleAgent(
    name="Администратор",
    llm=llm,
    system_prompt="""Ты администратор службы поддержки, в твои обязанности входит：
1. Анализировать тип вопроса клиента（технический или по продажам）
2. Использовать подходящий инструмент（tech_expert или sales_advisor）для получения ответа
3. Обобщить ответ и вернуть клиенту

Доступные инструменты：
- tech_expert: отвечает на технические вопросы
- sales_advisor: отвечает на вопросы по продажам

Сохраняй вежливость и профессионализм."""
)

# Добавляем инструменты A2A
receptionist.add_tool(tech_tool)
receptionist.add_tool(sales_tool)

print("Агент-администратор создан")
print("Интегрированы инструменты A2A: tech_expert, sales_advisor")

# ============================================================
# 5. Тестируем интегрированную систему
# ============================================================

print("\n" + "="*60)
print("Тестируем интеграцию A2A + SimpleAgent")
print("="*60)

# Тестовые вопросы
test_questions = [
    "Есть ли у вас скидки или акции на продукты?",
    "Как настроить SSL-сертификат для сервера?",
    "Хочу узнать о тарифных планах"
]

for i, question in enumerate(test_questions, 1):
    print(f"\nВопрос {i}: {question}")
    print("-" * 60)

    try:
        # Используем метод run SimpleAgent
        response = receptionist.run(question)
        print(f"Ответ: {response}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

    print()

# ============================================================
# 6. Поддерживаем работу сервисов
# ============================================================

print("="*60)
print("Система продолжает работу")
print("="*60)
print("Вы можете продолжить тестирование или нажать Ctrl+C для остановки\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nСистема остановлена")
