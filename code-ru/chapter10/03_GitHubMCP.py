"""
Пример GitHub MCP-сервиса

Примечание：необходимо задать переменную окружения
    Windows: $env:GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
    Linux/macOS: export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
"""

from hello_agents.tools import MCPTool

# Создаём инструмент GitHub MCP
github_tool = MCPTool(
    server_command=["npx", "-y", "@modelcontextprotocol/server-github"]
)

# 1. Список доступных инструментов
print("Доступные инструменты：")
result = github_tool.run({"action": "list_tools"})
print(result)

# 2. Поиск репозиториев
print("\nПоиск репозиториев：")
result = github_tool.run({
    "action": "call_tool",
    "tool_name": "search_repositories",
    "arguments": {
        "query": "AI agents language:python",
        "page": 1,
        "perPage": 3
    }
})
print(result)
