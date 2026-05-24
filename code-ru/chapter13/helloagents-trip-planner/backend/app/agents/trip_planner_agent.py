"""Система планирования путешествий с несколькими агентами"""

import json
from typing import Dict, Any, List
from hello_agents import SimpleAgent
from hello_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings

# ============ Промпты агентов ============

ATTRACTION_AGENT_PROMPT = """Ты эксперт по поиску достопримечательностей. Твоя задача — искать подходящие достопримечательности по городу и предпочтениям пользователя.

**Важно:**
Для поиска достопримечательностей необходимо использовать инструменты! Не придумывай информацию самостоятельно!

**Формат вызова инструмента:**
При использовании инструмента maps_text_search строго соблюдай следующий формат:
`[TOOL_CALL:amap_maps_text_search:keywords=ключевые слова,city=название города]`

**Примеры:**
Пользователь: "Найди исторические и культурные достопримечательности в Москве"
Твой ответ: [TOOL_CALL:amap_maps_text_search:keywords=исторические,city=Москва]

Пользователь: "Найди парки в Санкт-Петербурге"
Твой ответ: [TOOL_CALL:amap_maps_text_search:keywords=парк,city=Санкт-Петербург]

**Примечания:**
1. Инструменты обязательны — не отвечай напрямую
2. Формат должен быть точным, включая квадратные скобки и двоеточия
3. Параметры разделяются запятой
"""

WEATHER_AGENT_PROMPT = """Ты эксперт по запросу погоды. Твоя задача — запрашивать информацию о погоде в указанном городе.

**Важно:**
Для получения погоды необходимо использовать инструменты! Не придумывай информацию о погоде самостоятельно!

**Формат вызова инструмента:**
При использовании инструмента maps_weather строго соблюдай следующий формат:
`[TOOL_CALL:amap_maps_weather:city=название города]`

**Примеры:**
Пользователь: "Узнай погоду в Москве"
Твой ответ: [TOOL_CALL:amap_maps_weather:city=Москва]

Пользователь: "Какая погода в Санкт-Петербурге"
Твой ответ: [TOOL_CALL:amap_maps_weather:city=Санкт-Петербург]

**Примечания:**
1. Инструменты обязательны — не отвечай напрямую
2. Формат должен быть точным, включая квадратные скобки и двоеточия
"""

HOTEL_AGENT_PROMPT = """Ты эксперт по рекомендации отелей. Твоя задача — рекомендовать подходящие отели по городу и расположению достопримечательностей.

**Важно:**
Для поиска отелей необходимо использовать инструменты! Не придумывай информацию об отелях самостоятельно!

**Формат вызова инструмента:**
При использовании инструмента maps_text_search для поиска отелей строго соблюдай следующий формат:
`[TOOL_CALL:amap_maps_text_search:keywords=отель,city=название города]`

**Примеры:**
Пользователь: "Найди отели в Москве"
Твой ответ: [TOOL_CALL:amap_maps_text_search:keywords=отель,city=Москва]

**Примечания:**
1. Инструменты обязательны — не отвечай напрямую
2. Формат должен быть точным, включая квадратные скобки и двоеточия
3. В ключевых словах используй "отель" или "гостиница"
"""

PLANNER_AGENT_PROMPT = """Ты эксперт по планированию маршрутов. Твоя задача — на основе информации о достопримечательностях и погоде сформировать детальный план путешествия.

Строго верни план путешествия в следующем JSON-формате:
```json
{
  "city": "Название города",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "Обзор маршрута на 1-й день",
      "transportation": "Способ передвижения",
      "accommodation": "Тип размещения",
      "hotel": {
        "name": "Название отеля",
        "address": "Адрес отеля",
        "location": {"longitude": 37.617, "latitude": 55.755},
        "price_range": "3000-5000 руб.",
        "rating": "4.5",
        "distance": "2 км от достопримечательности",
        "type": "Экономичный отель",
        "estimated_cost": 4000
      },
      "attractions": [
        {
          "name": "Название достопримечательности",
          "address": "Подробный адрес",
          "location": {"longitude": 37.617, "latitude": 55.755},
          "visit_duration": 120,
          "description": "Подробное описание достопримечательности",
          "category": "Категория",
          "ticket_price": 500
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "Рекомендация на завтрак", "description": "Описание завтрака", "estimated_cost": 300},
        {"type": "lunch", "name": "Рекомендация на обед", "description": "Описание обеда", "estimated_cost": 500},
        {"type": "dinner", "name": "Рекомендация на ужин", "description": "Описание ужина", "estimated_cost": 800}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "Ясно",
      "night_weather": "Облачно",
      "day_temp": 20,
      "night_temp": 12,
      "wind_direction": "Южный",
      "wind_power": "1-3"
    }
  ],
  "overall_suggestions": "Общие рекомендации",
  "budget": {
    "total_attractions": 1500,
    "total_hotels": 12000,
    "total_meals": 4800,
    "total_transportation": 2000,
    "total": 20300
  }
}
```

**Важно:**
1. Массив weather_info должен содержать информацию о погоде на каждый день
2. Температура должна быть чистым числом (без единиц °C и т.п.)
3. Планируй 2-3 достопримечательности на каждый день
4. Учитывай расстояния между достопримечательностями и время посещения
5. Каждый день должен включать завтрак, обед и ужин
6. Предоставляй практичные советы для путешествия
7. **Обязательно включи информацию о бюджете**:
   - Цены на билеты (ticket_price)
   - Ориентировочные расходы на питание (estimated_cost)
   - Ориентировочные расходы на отель (estimated_cost)
   - Сводка бюджета (budget) с итогами по каждой категории
"""


class MultiAgentTripPlanner:
    """Система планирования путешествий с несколькими агентами"""

    def __init__(self):
        """Инициализация системы с несколькими агентами"""
        print("🔄 Начало инициализации системы планирования путешествий с несколькими агентами...")

        try:
            settings = get_settings()
            self.llm = get_llm()

            # Создаём общий MCP-инструмент (создаётся только один раз)
            print("  - Создание общего MCP-инструмента...")
            self.amap_tool = MCPTool(
                name="amap",
                description="Сервис карт AMap",
                server_command=["uvx", "amap-mcp-server"],
                env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
                auto_expand=True
            )
            self.amap_tool.expandable=True

            # Создаём агента поиска достопримечательностей
            print("  - Создание агента поиска достопримечательностей...")
            self.attraction_agent = SimpleAgent(
                name="Эксперт по достопримечательностям",
                llm=self.llm,
                system_prompt=ATTRACTION_AGENT_PROMPT
            )
            self.attraction_agent.add_tool(self.amap_tool)

            # Создаём агента запроса погоды
            print("  - Создание агента запроса погоды...")
            self.weather_agent = SimpleAgent(
                name="Эксперт по погоде",
                llm=self.llm,
                system_prompt=WEATHER_AGENT_PROMPT
            )
            self.weather_agent.add_tool(self.amap_tool)

            # Создаём агента рекомендации отелей
            print("  - Создание агента рекомендации отелей...")
            self.hotel_agent = SimpleAgent(
                name="Эксперт по отелям",
                llm=self.llm,
                system_prompt=HOTEL_AGENT_PROMPT
            )
            self.hotel_agent.add_tool(self.amap_tool)

            # Создаём агента планирования маршрутов (инструменты не нужны)
            print("  - Создание агента планирования маршрутов...")
            self.planner_agent = SimpleAgent(
                name="Эксперт по планированию маршрутов",
                llm=self.llm,
                system_prompt=PLANNER_AGENT_PROMPT
            )

            print(f"✅ Система с несколькими агентами успешно инициализирована")
            print(f"   Агент поиска достопримечательностей: {len(self.attraction_agent.list_tools())} инструментов")
            print(f"   Агент запроса погоды: {len(self.weather_agent.list_tools())} инструментов")
            print(f"   Агент рекомендации отелей: {len(self.hotel_agent.list_tools())} инструментов")

        except Exception as e:
            print(f"❌ Ошибка инициализации системы с несколькими агентами: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        Генерация плана путешествия с помощью совместной работы нескольких агентов

        Args:
            request: Запрос на планирование путешествия

        Returns:
            План путешествия
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 Начало совместного планирования путешествия...")
            print(f"Направление: {request.city}")
            print(f"Даты: {request.start_date} — {request.end_date}")
            print(f"Дней: {request.travel_days}")
            print(f"Предпочтения: {', '.join(request.preferences) if request.preferences else 'не указаны'}")
            print(f"{'='*60}\n")

            # Шаг 1: Агент поиска достопримечательностей
            print("📍 Шаг 1: Поиск достопримечательностей...")
            attraction_query = self._build_attraction_query(request)
            attraction_response = self.attraction_agent.run(attraction_query)
            print(f"Результаты поиска достопримечательностей: {attraction_response[:200]}...\n")

            # Шаг 2: Агент запроса погоды
            print("🌤️  Шаг 2: Запрос погоды...")
            weather_query = f"Запроси информацию о погоде в городе {request.city}"
            weather_response = self.weather_agent.run(weather_query)
            print(f"Результаты запроса погоды: {weather_response[:200]}...\n")

            # Шаг 3: Агент рекомендации отелей
            print("🏨 Шаг 3: Поиск отелей...")
            hotel_query = f"Найди отели типа «{request.accommodation}» в городе {request.city}"
            hotel_response = self.hotel_agent.run(hotel_query)
            print(f"Результаты поиска отелей: {hotel_response[:200]}...\n")

            # Шаг 4: Агент планирования маршрутов объединяет информацию
            print("📋 Шаг 4: Формирование плана маршрута...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response)
            planner_response = self.planner_agent.run(planner_query)
            print(f"Результат планирования маршрута: {planner_response[:300]}...\n")

            # Разбираем итоговый план
            trip_plan = self._parse_response(planner_response, request)

            print(f"{'='*60}")
            print(f"✅ План путешествия успешно сформирован!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ Ошибка формирования плана путешествия: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)

    def _build_attraction_query(self, request: TripRequest) -> str:
        """Формирует поисковый запрос достопримечательностей — сразу с вызовом инструмента"""
        keywords = []
        if request.preferences:
            # Берём только первое предпочтение как ключевое слово
            keywords = request.preferences[0]
        else:
            keywords = "достопримечательность"

        # Возвращаем сразу в формате вызова инструмента
        query = f"Используй инструмент amap_maps_text_search для поиска достопримечательностей по запросу «{keywords}» в городе {request.city}.\n[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """Формирует запрос для агента планирования маршрутов"""
        query = f"""Составь план путешествия на {request.travel_days} дней по городу {request.city} на основе следующей информации:

**Основные параметры:**
- Город: {request.city}
- Даты: {request.start_date} — {request.end_date}
- Дней: {request.travel_days}
- Транспорт: {request.transportation}
- Размещение: {request.accommodation}
- Предпочтения: {', '.join(request.preferences) if request.preferences else 'не указаны'}

**Информация о достопримечательностях:**
{attractions}

**Информация о погоде:**
{weather}

**Информация об отелях:**
{hotels}

**Требования:**
1. Планируй 2-3 достопримечательности на каждый день
2. Каждый день должен включать завтрак, обед и ужин
3. Для каждого дня рекомендуй конкретный отель (выбирай из предоставленных данных)
4. Учитывай расстояния между достопримечательностями и способ передвижения
5. Верни полные данные в формате JSON
6. Координаты достопримечательностей должны быть точными
"""
        if request.free_text_input:
            query += f"\n**Дополнительные пожелания:** {request.free_text_input}"

        return query

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        Разбирает ответ агента

        Args:
            response: Текст ответа агента
            request: Исходный запрос

        Returns:
            План путешествия
        """
        try:
            # Пытаемся извлечь JSON из ответа
            # Ищем блок с кодом JSON
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # Ищем объект JSON напрямую
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("JSON-данные не найдены в ответе")

            # Разбираем JSON
            data = json.loads(json_str)

            # Преобразуем в объект TripPlan
            trip_plan = TripPlan(**data)

            return trip_plan

        except Exception as e:
            print(f"⚠️  Ошибка разбора ответа: {str(e)}")
            print(f"   Будет использован резервный вариант плана")
            return self._create_fallback_plan(request)

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """Создаёт резервный план (при сбое агента)"""
        from datetime import datetime, timedelta

        # Разбираем дату
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")

        # Создаём дневные маршруты
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)

            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"День {i+1} маршрута",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"Достопримечательность {j+1} в {request.city}",
                        address=f"г. {request.city}",
                        location=Location(longitude=37.617 + i*0.01 + j*0.005, latitude=55.755 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"Известная достопримечательность в городе {request.city}",
                        category="Достопримечательность"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"Завтрак — день {i+1}", description="Местный завтрак"),
                    Meal(type="lunch", name=f"Обед — день {i+1}", description="Рекомендация на обед"),
                    Meal(type="dinner", name=f"Ужин — день {i+1}", description="Рекомендация на ужин")
                ]
            )
            days.append(day_plan)

        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"Это запланированный маршрут по {request.city} на {request.travel_days} дней. Рекомендуем заранее уточнить часы работы достопримечательностей."
        )


# Глобальный экземпляр системы с несколькими агентами
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """Возвращает экземпляр системы планирования путешествий (одиночный объект)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner
