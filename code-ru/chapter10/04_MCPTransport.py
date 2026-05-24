from hello_agents.tools import MCPTool

# 1. Memory Transport - передача через память（для тестирования）
# Не указываем параметры, используем встроенный демо-сервер
mcp_tool = MCPTool()

# 2. Stdio Transport - передача через стандартный ввод/вывод（для локальной разработки）
# Запуск локального сервера с помощью списка команд
mcp_tool = MCPTool(server_command=["python", "examples/mcp_example_server.py"])

# 3. Stdio Transport with Args - передача по команде с аргументами
# Можно передавать дополнительные аргументы
mcp_tool = MCPTool(server_command=["python", "examples/mcp_example_server.py", "--debug"])

# 4. Stdio Transport - серверы сообщества（через npx）
# Запуск серверов MCP сообщества через npx
mcp_tool = MCPTool(server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

# 5. HTTP/SSE/StreamableHTTP Transport
# Примечание：MCPTool в основном используется для Stdio и Memory-передачи
# Для удалённых передач HTTP/SSE рекомендуется использовать MCPClient напрямую

from hello_agents.tools import MCPTool

# Используем встроенный демо-сервер（Memory-передача）
mcp_tool = MCPTool()

# Список доступных инструментов
result = mcp_tool.run({"action": "list_tools"})
print(result)

# Вызов инструмента
result = mcp_tool.run({
    "action": "call_tool",
    "tool_name": "add",
    "arguments": {"a": 10, "b": 20}
})
print(result)

from hello_agents.tools import MCPTool

# Способ 1：использование собственного Python-сервера
mcp_tool = MCPTool(server_command=["python", "my_mcp_server.py"])

# Способ 2：использование серверов сообщества（файловая система）
mcp_tool = MCPTool(server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

# Список инструментов
result = mcp_tool.run({"action": "list_tools"})
print(result)

# Вызов инструмента
result = mcp_tool.run({
    "action": "call_tool",
    "tool_name": "read_file",
    "arguments": {"path": "my_README.md"}
})
print(result)


# Примечание：MCPTool в основном используется для Stdio и Memory-передачи
# Для удалённых передач HTTP/SSE рекомендуется использовать низкоуровневый MCPClient

import asyncio
from hello_agents.protocols.mcp.client import MCPClient

async def test_http_transport():
    # Подключение к удалённому HTTP MCP-серверу
    client = MCPClient("http://api.example.com/mcp")

    async with client:
        # Получаем информацию о сервере
        tools = await client.list_tools()
        print(f"Инструменты удалённого сервера: {len(tools)} шт.")

        # Вызов удалённого инструмента
        result = await client.call_tool("process_data", {
            "data": "Hello, World!",
            "operation": "uppercase"
        })
        print(f"Результат удалённой обработки: {result}")

# Примечание：требуется реальный HTTP MCP-сервер
# asyncio.run(test_http_transport())
