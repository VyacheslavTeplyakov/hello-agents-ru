"""
10.3.3 Использование инструмента A2A в HelloAgents
(1) Создание серверной части A2A Agent
"""

from hello_agents.protocols import A2AServer
import threading
import time

# Создаём сервис агента-исследователя
researcher = A2AServer(
    name="researcher",
    description="Агент, отвечающий за поиск и анализ материалов",
    version="1.0.0"
)

# Определяем навык
@researcher.skill("research")
def handle_research(text: str) -> str:
    """Обработка запроса на исследование"""
    import re
    match = re.search(r'research\s+(.+)', text, re.IGNORECASE)
    topic = match.group(1).strip() if match else text

    # Реальная логика исследования（здесь упрощена）
    result = {
        "topic": topic,
        "findings": f"Результаты исследования по теме {topic}...",
        "sources": ["Источник 1", "Источник 2", "Источник 3"]
    }
    return str(result)

# Запускаем сервис в фоновом режиме
def start_server():
    researcher.run(host="localhost", port=5000)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Сервис агента-исследователя запущен на http://localhost:5000")

    # Поддерживаем работу программы
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nСервис остановлен")
