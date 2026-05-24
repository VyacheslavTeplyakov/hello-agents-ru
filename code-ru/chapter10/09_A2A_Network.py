"""
10.3.3 Использование инструмента A2A в HelloAgents
(3) Создание сети агентов
"""

from hello_agents.protocols import A2AServer, A2AClient
import threading
import time

# 1. Создаём несколько сервисов агентов
researcher = A2AServer(
    name="researcher",
    description="Исследователь"
)

@researcher.skill("research")
def do_research(text: str) -> str:
    import re
    match = re.search(r'research\s+(.+)', text, re.IGNORECASE)
    topic = match.group(1).strip() if match else text
    return str({"topic": topic, "findings": f"Результаты исследования по теме {topic}"})

writer = A2AServer(
    name="writer",
    description="Автор"
)

@writer.skill("write")
def write_article(text: str) -> str:
    import re
    match = re.search(r'write\s+(.+)', text, re.IGNORECASE)
    content = match.group(1).strip() if match else text

    # Пытаемся разобрать данные исследования
    try:
        data = eval(content)
        topic = data.get("topic", "Неизвестная тема")
        findings = data.get("findings", "Нет результатов исследования")
    except:
        topic = "Неизвестная тема"
        findings = content

    return f"# {topic}\n\nНа основе исследования：{findings}\n\nСодержимое статьи..."

editor = A2AServer(
    name="editor",
    description="Редактор"
)

@editor.skill("edit")
def edit_article(text: str) -> str:
    import re
    match = re.search(r'edit\s+(.+)', text, re.IGNORECASE)
    article = match.group(1).strip() if match else text

    result = {
        "article": article + "\n\n[Отредактировано и улучшено]",
        "feedback": "Качество статьи хорошее",
        "approved": True
    }
    return str(result)

# 2. Запускаем все сервисы
threading.Thread(target=lambda: researcher.run(port=5000), daemon=True).start()
threading.Thread(target=lambda: writer.run(port=5001), daemon=True).start()
threading.Thread(target=lambda: editor.run(port=5002), daemon=True).start()
time.sleep(2)  # Ожидаем запуска сервисов

# 3. Создаём клиентов для подключения к каждому агенту
researcher_client = A2AClient("http://localhost:5000")
writer_client = A2AClient("http://localhost:5001")
editor_client = A2AClient("http://localhost:5002")

# 4. Процесс совместной работы
def create_content(topic):
    # Шаг 1：исследование
    research = researcher_client.execute_skill("research", f"research {topic}")
    research_data = research.get('result', '')

    # Шаг 2：написание
    article = writer_client.execute_skill("write", f"write {research_data}")
    article_content = article.get('result', '')

    # Шаг 3：редактирование
    final = editor_client.execute_skill("edit", f"edit {article_content}")
    return final.get('result', '')

# Использование
if __name__ == "__main__":
    result = create_content("применение ИИ в медицине")
    print(f"\nИтоговый результат：\n{result}")
