#!/usr/bin/env python3
"""Тестирование MCP-сервера запроса погоды"""

import asyncio
import json
import os
from hello_agents.protocols import MCPClient


async def test_weather_server():
    server_script = os.path.join(os.path.dirname(__file__), "14_weather_mcp_server.py")
    client = MCPClient(["python", server_script])

    try:
        async with client:
            # Тест 1: Получить информацию о сервере
            info = json.loads(await client.call_tool("get_server_info", {}))
            print(f"Сервер: {info['name']} v{info['version']}")

            # Тест 2: Список поддерживаемых городов
            cities = json.loads(await client.call_tool("list_supported_cities", {}))
            print(f"Поддерживаемые города: {cities['count']} шт.")

            # Тест 3: Запрос погоды в Пекине
            weather = json.loads(await client.call_tool("get_weather", {"city": "北京"}))
            if "error" not in weather:
                print(f"\nПогода в Пекине: {weather['temperature']}°C, {weather['condition']}")

            # Тест 4: Запрос погоды в Шэньчжэне
            weather = json.loads(await client.call_tool("get_weather", {"city": "深圳"}))
            if "error" not in weather:
                print(f"Погода в Шэньчжэне: {weather['temperature']}°C, {weather['condition']}")

            print("\n✅ Все тесты завершены!")

    except Exception as e:
        print(f"❌ Тест провален: {e}")


if __name__ == "__main__":
    asyncio.run(test_weather_server())
