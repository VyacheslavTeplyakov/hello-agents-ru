"""
10.3.4 Использование инструмента A2A в агенте
(1) Использование обёртки A2ATool
"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import A2ATool
from dotenv import load_dotenv

load_dotenv()
llm = HelloAgentsLLM()

# Предполагается, что сервис агента-исследователя уже запущен на http://localhost:5000

# Создаём агента-координатора
coordinator = SimpleAgent(name="Координатор", llm=llm)

# Добавляем инструмент A2A, подключаемся к агенту-исследователю
researcher_tool = A2ATool(agent_url="http://localhost:5000")
coordinator.add_tool(researcher_tool)

# Координатор может вызывать агента-исследователя
# Используем action="ask" для отправки вопроса агенту
response = coordinator.run("Используй инструмент a2a, задай агенту вопрос：исследуй применение ИИ в сфере образования")
print(response)
