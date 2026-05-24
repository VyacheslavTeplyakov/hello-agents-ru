"""
10.3.4 Использование инструмента A2A в агенте
(3) Продвинутое использование：переговоры между агентами
"""

from hello_agents.protocols import A2AServer, A2AClient
import threading
import time

# Создаём двух агентов, которые должны провести переговоры
agent1 = A2AServer(
    name="agent1",
    description="Agent 1"
)

@agent1.skill("propose")
def handle_proposal(text: str) -> str:
    """Обработка предложения о переговорах"""
    import re
    import json

    # Разбираем предложение
    match = re.search(r'propose\s+(.+)', text, re.IGNORECASE)
    proposal_str = match.group(1).strip() if match else text

    try:
        proposal = eval(proposal_str)
        task = proposal.get("task")
        deadline = proposal.get("deadline")

        # Оцениваем предложение
        if deadline >= 7:  # Требуется минимум 7 дней
            result = {"accepted": True, "message": "Предложение принято"}
        else:
            result = {
                "accepted": False,
                "message": "Слишком сжатые сроки",
                "counter_proposal": {"deadline": 7}
            }
        return str(result)
    except:
        return str({"accepted": False, "message": "Неверный формат предложения"})

agent2 = A2AServer(
    name="agent2",
    description="Agent 2"
)

@agent2.skill("negotiate")
def negotiate_task(text: str) -> str:
    """Инициирование переговоров"""
    import re

    # Разбираем задачу и срок
    match = re.search(r'negotiate\s+task:(.+?)\s+deadline:(\d+)', text, re.IGNORECASE)
    if match:
        task = match.group(1).strip()
        deadline = int(match.group(2))

        # Отправляем предложение agent1
        proposal = {"task": task, "deadline": deadline}
        return str({"status": "negotiating", "proposal": proposal})
    else:
        return str({"status": "error", "message": "Неверный запрос на переговоры"})

# Запускаем сервисы
if __name__ == "__main__":
    threading.Thread(target=lambda: agent1.run(port=7000), daemon=True).start()
    threading.Thread(target=lambda: agent2.run(port=7001), daemon=True).start()
    time.sleep(2)

    # Тестируем процесс переговоров
    client1 = A2AClient("http://localhost:7000")
    client2 = A2AClient("http://localhost:7001")

    # Agent2 инициирует переговоры
    negotiation = client2.execute_skill("negotiate", "negotiate task:разработка новой функции deadline:5")
    print(f"Запрос на переговоры：{negotiation.get('result')}")

    # Agent1 оценивает предложение
    proposal = client1.execute_skill("propose", "propose {'task': 'разработка новой функции', 'deadline': 5}")
    print(f"Оценка предложения：{proposal.get('result')}")

    # Поддерживаем работу сервисов
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nСервисы остановлены")
