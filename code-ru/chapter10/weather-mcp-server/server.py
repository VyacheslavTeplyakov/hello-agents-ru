#!/usr/bin/env python3
"""MCP-сервер запроса погоды"""

import json
import requests
import os
from datetime import datetime
from typing import Dict, Any
from hello_agents.protocols import MCPServer

# Создаём MCP-сервер
weather_server = MCPServer(name="weather-server", description="Сервис запроса реальной погоды")

CITY_MAP = {
    "Пекин": "Beijing", "Шанхай": "Shanghai", "Гуанчжоу": "Guangzhou",
    "Шэньчжэнь": "Shenzhen", "Ханчжоу": "Hangzhou", "Чэнду": "Chengdu",
    "Чунцин": "Chongqing", "Ухань": "Wuhan", "Сиань": "Xi'an",
    "Нанкин": "Nanjing", "Тяньцзинь": "Tianjin", "Сучжоу": "Suzhou"
}


def get_weather_data(city: str) -> Dict[str, Any]:
    """Получает данные о погоде с wttr.in"""
    city_en = CITY_MAP.get(city, city)
    url = f"https://wttr.in/{city_en}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data["current_condition"][0]

    return {
        "city": city,
        "temperature": float(current["temp_C"]),
        "feels_like": float(current["FeelsLikeC"]),
        "humidity": int(current["humidity"]),
        "condition": current["weatherDesc"][0]["value"],
        "wind_speed": round(float(current["windspeedKmph"]) / 3.6, 1),
        "visibility": float(current["visibility"]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# Определяем функции-инструменты
def get_weather(city: str) -> str:
    """Получает текущую погоду в указанном городе"""
    try:
        weather_data = get_weather_data(city)
        return json.dumps(weather_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "city": city}, ensure_ascii=False)


def list_supported_cities() -> str:
    """Перечисляет все поддерживаемые города"""
    result = {"cities": list(CITY_MAP.keys()), "count": len(CITY_MAP)}
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_server_info() -> str:
    """Получает информацию о сервере"""
    info = {
        "name": "Weather MCP Server",
        "version": "1.0.0",
        "tools": ["get_weather", "list_supported_cities", "get_server_info"]
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


# Регистрируем инструменты на сервере
weather_server.add_tool(get_weather)
weather_server.add_tool(list_supported_cities)
weather_server.add_tool(get_server_info)


if __name__ == "__main__":
    # Smithery требует HTTP-транспорт на порту из переменной окружения PORT
    port = int(os.getenv("PORT", 8081))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🌤️  Запуск Weather MCP Server...")
    print(f"📡 Транспорт: HTTP")
    print(f"🌐 Хост: {host}")
    print(f"🔌 Порт: {port}")
    print(f"🔗 Эндпоинт: http://{host}:{port}/mcp")
    print(f"✨ Готов к обработке запросов погоды!")

    # Запускаем с HTTP-транспортом (требуется Smithery)
    weather_server.run(transport="http", host=host, port=port)
