"""Обёртка над MCP-сервисом карт AMap"""

from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

# Глобальный экземпляр MCP-инструмента
_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    """
    Возвращает экземпляр MCP-инструмента карт AMap (одиночный объект)

    Returns:
        Экземпляр MCPTool
    """
    global _amap_mcp_tool

    if _amap_mcp_tool is None:
        settings = get_settings()

        if not settings.amap_api_key:
            raise ValueError("API Key AMap не настроен, укажите AMAP_API_KEY в файле .env")

        # Создаём MCP-инструмент
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="Сервис карт AMap: поиск POI, построение маршрутов, запрос погоды и другие функции",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True  # Автоматически разворачивает в независимые инструменты
        )

        print(f"✅ MCP-инструмент карт AMap успешно инициализирован")
        print(f"   Количество инструментов: {len(_amap_mcp_tool._available_tools)}")

        # Печатаем список доступных инструментов
        if _amap_mcp_tool._available_tools:
            print("   Доступные инструменты:")
            for tool in _amap_mcp_tool._available_tools[:5]:  # Печатаем первые 5
                print(f"     - {tool.get('name', 'unknown')}")
            if len(_amap_mcp_tool._available_tools) > 5:
                print(f"     ... и ещё {len(_amap_mcp_tool._available_tools) - 5} инструментов")

    return _amap_mcp_tool


class AmapService:
    """Класс-обёртка над сервисом карт AMap"""

    def __init__(self):
        """Инициализация сервиса"""
        self.mcp_tool = get_amap_mcp_tool()

    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        Поиск POI

        Args:
            keywords: Ключевые слова для поиска
            city: Город
            citylimit: Ограничить поиск пределами города

        Returns:
            Список объектов POI
        """
        try:
            # Вызываем MCP-инструмент
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_text_search",
                "arguments": {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": str(citylimit).lower()
                }
            })

            # Разбираем результат
            # Примечание: MCP-инструмент возвращает строку, её нужно разобрать
            # Здесь упрощённая обработка, в реальности следует разбирать JSON
            print(f"Результаты поиска POI: {result[:200]}...")  # Печатаем первые 200 символов

            # TODO: Разобрать реальные данные POI
            return []

        except Exception as e:
            print(f"❌ Ошибка поиска POI: {str(e)}")
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        Запрос погоды

        Args:
            city: Название города

        Returns:
            Список объектов с информацией о погоде
        """
        try:
            # Вызываем MCP-инструмент
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": city
                }
            })

            print(f"Результаты запроса погоды: {result[:200]}...")

            # TODO: Разобрать реальные данные о погоде
            return []

        except Exception as e:
            print(f"❌ Ошибка запроса погоды: {str(e)}")
            return []

    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        Построение маршрута

        Args:
            origin_address: Адрес начальной точки
            destination_address: Адрес конечной точки
            origin_city: Город начальной точки
            destination_city: Город конечной точки
            route_type: Тип маршрута (walking/driving/transit)

        Returns:
            Информация о маршруте
        """
        try:
            # Выбираем инструмент по типу маршрута
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }

            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")

            # Формируем параметры
            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address
            }

            # Общественный транспорт требует параметры города
            if route_type == "transit":
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            else:
                # Для других типов маршрутов параметры города повышают точность
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city

            # Вызываем MCP-инструмент
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments
            })

            print(f"Результаты построения маршрута: {result[:200]}...")

            # TODO: Разобрать реальные данные о маршруте
            return {}

        except Exception as e:
            print(f"❌ Ошибка построения маршрута: {str(e)}")
            return {}

    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        Геокодирование (адрес → координаты)

        Args:
            address: Адрес
            city: Город

        Returns:
            Географические координаты
        """
        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_geo",
                "arguments": arguments
            })

            print(f"Результаты геокодирования: {result[:200]}...")

            # TODO: Разобрать реальные данные о координатах
            return None

        except Exception as e:
            print(f"❌ Ошибка геокодирования: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        Получение деталей POI

        Args:
            poi_id: Идентификатор POI

        Returns:
            Подробная информация об объекте POI
        """
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_search_detail",
                "arguments": {
                    "id": poi_id
                }
            })

            print(f"Детали POI: {result[:200]}...")

            # Разбираем результат и извлекаем фотографии
            import json
            import re

            # Пытаемся извлечь JSON из результата
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data

            return {"raw": result}

        except Exception as e:
            print(f"❌ Ошибка получения деталей POI: {str(e)}")
            return {}


# Создаём глобальный экземпляр сервиса
_amap_service = None


def get_amap_service() -> AmapService:
    """Возвращает экземпляр сервиса карт AMap (одиночный объект)"""
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service
