import asyncio
from hello_agents.protocols import MCPClient

async def connect_to_server():
    # Способ 1：подключение к серверу файловой системы, предоставленному сообществом
    # npx автоматически скачает и запустит пакет @modelcontextprotocol/server-filesystem
    client = MCPClient([
        "npx", "-y",
        "@modelcontextprotocol/server-filesystem",
        "."  # указать корневой каталог
    ])

    # Используем async with для корректного закрытия соединения
    async with client:
        # Используем client здесь
        tools = await client.list_tools()
        print(f"Доступные инструменты: {[t['name'] for t in tools]}")

    # Способ 2：подключение к собственному Python MCP-серверу
    client = MCPClient(["python", "my_mcp_server.py"])
    async with client:
        # Используем client...
        pass

# Запуск асинхронной функции
asyncio.run(connect_to_server())


async def discover_tools():
    client = MCPClient(["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

    async with client:
        # Получаем все доступные инструменты
        tools = await client.list_tools()

        print(f"Сервер предоставляет {len(tools)} инструментов：")
        for tool in tools:
            print(f"\nНазвание инструмента: {tool['name']}")
            print(f"Описание: {tool.get('description', 'нет описания')}")

            # Выводим информацию о параметрах
            if 'inputSchema' in tool:
                schema = tool['inputSchema']
                if 'properties' in schema:
                    print("Параметры:")
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'any')
                        param_desc = param_info.get('description', '')
                        print(f"  - {param_name} ({param_type}): {param_desc}")

asyncio.run(discover_tools())

# Пример вывода：
# Сервер предоставляет 5 инструментов：
#
# Название инструмента: read_file
# Описание: чтение содержимого файла
# Параметры:
#   - path (string): путь к файлу
#
# Название инструмента: write_file
# Описание: запись содержимого в файл
# Параметры:
#   - path (string): путь к файлу
#   - content (string): содержимое файла


async def use_tools():
    client = MCPClient(["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

    async with client:
        # Читаем файл
        result = await client.call_tool("read_file", {"path": "my_README.md"})
        print(f"Содержимое файла：\n{result}")

        # Просматриваем каталог
        result = await client.call_tool("list_directory", {"path": "."})
        print(f"Файлы в текущем каталоге：{result}")

        # Записываем файл
        result = await client.call_tool("write_file", {
            "path": "output.txt",
            "content": "Hello from MCP!"
        })
        print(f"Результат записи：{result}")

asyncio.run(use_tools())

async def safe_tool_call():
    client = MCPClient(["npx", "-y", "@modelcontextprotocol/server-filesystem", "."])

    async with client:
        try:
            # Пытаемся прочитать файл, который может не существовать
            result = await client.call_tool("read_file", {"path": "nonexistent.txt"})
            print(result)
        except Exception as e:
            print(f"Вызов инструмента завершился ошибкой: {e}")
            # Можно выбрать повтор, использование значения по умолчанию или сообщение об ошибке пользователю

asyncio.run(safe_tool_call())
