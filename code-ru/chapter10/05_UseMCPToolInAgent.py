from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool

print("=" * 70)
print("Способ 1：использование встроенного демо-сервера")
print("=" * 70)

agent = SimpleAgent(name="Ассистент", llm=HelloAgentsLLM())

# Конфигурация не требуется, встроенный демо-сервер используется автоматически
# Встроенный сервер предоставляет：add, subtract, multiply, divide, greet, get_system_info
mcp_tool = MCPTool()  # по умолчанию name="mcp"
agent.add_tool(mcp_tool)

# Агент может использовать встроенные инструменты
response = agent.run("Вычисли 123 + 456")
print(response)  # Агент автоматически вызовет инструмент add

print("\n" + "=" * 70)
print("Способ 2：подключение к внешним MCP-серверам（использование нескольких серверов）")
print("=" * 70)

# Важно：задайте разные имена для каждого MCP-сервера, чтобы избежать конфликтов имён инструментов

# Пример 1：подключение к серверу файловой системы, предоставленному сообществом
fs_tool = MCPTool(
    name="filesystem",  # задаём уникальное имя
    description="Доступ к локальной файловой системе",
    server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]
)
agent.add_tool(fs_tool)

# Пример 2：подключение к собственному Python MCP-серверу
# О том, как написать собственный MCP-сервер, см. раздел 10.5
custom_tool = MCPTool(
    name="custom_server",  # используем другое имя
    description="Сервер с пользовательской бизнес-логикой",
    server_command=["python", "my_mcp_server.py"]
)
agent.add_tool(custom_tool)

print("\nИнструменты текущего агента：")
print(f"- {mcp_tool.name}: {mcp_tool.description}")
print(f"- {fs_tool.name}: {fs_tool.description}")
print(f"- {custom_tool.name}: {custom_tool.description}")

# Агент теперь может автоматически использовать эти инструменты！
response = agent.run("Прочитай файл my_README.md и кратко изложи его основное содержание")
print(response)
