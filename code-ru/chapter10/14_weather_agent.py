"""Использование MCP-сервера погоды в агенте"""

import os
from dotenv import load_dotenv
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool

load_dotenv()


def create_weather_assistant():
    """Создаёт погодного ассистента"""
    llm = HelloAgentsLLM()

    assistant = SimpleAgent(
        name="Погодный ассистент",
        llm=llm,
        system_prompt="""Ты погодный ассистент, умеющий запрашивать погоду в городах.
Используй инструмент get_weather для запроса погоды, поддерживаются китайские названия городов.
"""
    )

    # Добавляем инструмент MCP для погоды
    server_script = os.path.join(os.path.dirname(__file__), "14_weather_mcp_server.py")
    weather_tool = MCPTool(server_command=["python", server_script])
    assistant.add_tool(weather_tool)

    return assistant


def demo():
    """Демонстрация"""
    assistant = create_weather_assistant()

    print("\nЗапрос погоды в Пекине:")
    response = assistant.run("Какая сегодня погода в Пекине?")
    print(f"Ответ: {response}\n")


def interactive():
    """Интерактивный режим"""
    assistant = create_weather_assistant()

    while True:
        user_input = input("\nВы: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            break
        response = assistant.run(user_input)
        print(f"Ассистент: {response}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo()
    else:
        interactive()
