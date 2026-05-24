"""
10.3.3 Использование инструмента A2A в HelloAgents
(2) Создание клиента A2A Agent
"""

from hello_agents.protocols import A2AClient
import time

# Ожидаем запуска сервера
time.sleep(1)

# Создаём клиента и подключаемся к агенту-исследователю
client = A2AClient("http://localhost:5000")

# Отправляем запрос на исследование
response = client.execute_skill("research", "research применение ИИ в медицине")
print(f"Получен ответ：{response.get('result')}")

# Вывод：
# Получен ответ：{'topic': 'применение ИИ в медицине', 'findings': 'Результаты исследования по теме применение ИИ в медицине...', 'sources': ['Источник 1', 'Источник 2', 'Источник 3']}
