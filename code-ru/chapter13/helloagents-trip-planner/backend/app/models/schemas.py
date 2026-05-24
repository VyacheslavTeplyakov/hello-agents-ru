"""Определения моделей данных"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import date


# ============ Модели запросов ============

class TripRequest(BaseModel):
    """Запрос на планирование путешествия"""
    city: str = Field(..., description="Город назначения", example="Москва")
    start_date: str = Field(..., description="Дата начала YYYY-MM-DD", example="2025-06-01")
    end_date: str = Field(..., description="Дата окончания YYYY-MM-DD", example="2025-06-03")
    travel_days: int = Field(..., description="Количество дней", ge=1, le=30, example=3)
    transportation: str = Field(..., description="Способ передвижения", example="Общественный транспорт")
    accommodation: str = Field(..., description="Предпочтения по размещению", example="Экономичный отель")
    preferences: List[str] = Field(default=[], description="Теги предпочтений путешествия", example=["История и культура", "Гастрономия"])
    free_text_input: Optional[str] = Field(default="", description="Дополнительные пожелания", example="Хочу посетить больше музеев")

    class Config:
        json_schema_extra = {
            "example": {
                "city": "Москва",
                "start_date": "2025-06-01",
                "end_date": "2025-06-03",
                "travel_days": 3,
                "transportation": "Общественный транспорт",
                "accommodation": "Экономичный отель",
                "preferences": ["История и культура", "Гастрономия"],
                "free_text_input": "Хочу посетить больше музеев"
            }
        }


class POISearchRequest(BaseModel):
    """Запрос на поиск POI"""
    keywords: str = Field(..., description="Ключевые слова для поиска", example="Кремль")
    city: str = Field(..., description="Город", example="Москва")
    citylimit: bool = Field(default=True, description="Ограничить поиск пределами города")


class RouteRequest(BaseModel):
    """Запрос на построение маршрута"""
    origin_address: str = Field(..., description="Адрес начальной точки", example="Москва, Красная площадь")
    destination_address: str = Field(..., description="Адрес конечной точки", example="Москва, Воробьёвы горы")
    origin_city: Optional[str] = Field(default=None, description="Город начальной точки")
    destination_city: Optional[str] = Field(default=None, description="Город конечной точки")
    route_type: str = Field(default="walking", description="Тип маршрута: walking/driving/transit")


# ============ Модели ответов ============

class Location(BaseModel):
    """Географические координаты"""
    longitude: float = Field(..., description="Долгота")
    latitude: float = Field(..., description="Широта")


class Attraction(BaseModel):
    """Информация о достопримечательности"""
    name: str = Field(..., description="Название достопримечательности")
    address: str = Field(..., description="Адрес")
    location: Location = Field(..., description="Координаты")
    visit_duration: int = Field(..., description="Рекомендуемое время посещения (минуты)")
    description: str = Field(..., description="Описание достопримечательности")
    category: Optional[str] = Field(default="Достопримечательность", description="Категория")
    rating: Optional[float] = Field(default=None, description="Рейтинг")
    photos: Optional[List[str]] = Field(default_factory=list, description="Список URL фотографий")
    poi_id: Optional[str] = Field(default="", description="Идентификатор POI")
    image_url: Optional[str] = Field(default=None, description="URL фотографии")
    ticket_price: int = Field(default=0, description="Цена билета (руб.)")


class Meal(BaseModel):
    """Информация о питании"""
    type: str = Field(..., description="Тип питания: breakfast/lunch/dinner/snack")
    name: str = Field(..., description="Название заведения")
    address: Optional[str] = Field(default=None, description="Адрес")
    location: Optional[Location] = Field(default=None, description="Координаты")
    description: Optional[str] = Field(default=None, description="Описание")
    estimated_cost: int = Field(default=0, description="Ориентировочная стоимость (руб.)")


class Hotel(BaseModel):
    """Информация об отеле"""
    name: str = Field(..., description="Название отеля")
    address: str = Field(default="", description="Адрес отеля")
    location: Optional[Location] = Field(default=None, description="Расположение отеля")
    price_range: str = Field(default="", description="Ценовой диапазон")
    rating: str = Field(default="", description="Рейтинг")
    distance: str = Field(default="", description="Расстояние до достопримечательности")
    type: str = Field(default="", description="Тип отеля")
    estimated_cost: int = Field(default=0, description="Ориентировочная стоимость (руб./ночь)")


class DayPlan(BaseModel):
    """Дневной маршрут"""
    date: str = Field(..., description="Дата YYYY-MM-DD")
    day_index: int = Field(..., description="Порядковый номер дня (начиная с 0)")
    description: str = Field(..., description="Описание дневного маршрута")
    transportation: str = Field(..., description="Способ передвижения")
    accommodation: str = Field(..., description="Размещение")
    hotel: Optional[Hotel] = Field(default=None, description="Рекомендуемый отель")
    attractions: List[Attraction] = Field(default=[], description="Список достопримечательностей")
    meals: List[Meal] = Field(default=[], description="Список приёмов пищи")


class WeatherInfo(BaseModel):
    """Информация о погоде"""
    date: str = Field(..., description="Дата YYYY-MM-DD")
    day_weather: str = Field(default="", description="Погода днём")
    night_weather: str = Field(default="", description="Погода ночью")
    day_temp: Union[int, str] = Field(default=0, description="Температура днём")
    night_temp: Union[int, str] = Field(default=0, description="Температура ночью")
    wind_direction: str = Field(default="", description="Направление ветра")
    wind_power: str = Field(default="", description="Сила ветра")

    @field_validator('day_temp', 'night_temp', mode='before')
    @classmethod
    def parse_temperature(cls, v):
        """Разбирает температуру, удаляя единицы измерения °C и т.п."""
        if isinstance(v, str):
            # Удаляем °C, ℃ и другие символы единиц
            v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
            try:
                return int(v)
            except ValueError:
                return 0
        return v


class Budget(BaseModel):
    """Информация о бюджете"""
    total_attractions: int = Field(default=0, description="Общая стоимость билетов")
    total_hotels: int = Field(default=0, description="Общая стоимость проживания")
    total_meals: int = Field(default=0, description="Общие расходы на питание")
    total_transportation: int = Field(default=0, description="Общие расходы на транспорт")
    total: int = Field(default=0, description="Итоговая сумма")


class TripPlan(BaseModel):
    """План путешествия"""
    city: str = Field(..., description="Город назначения")
    start_date: str = Field(..., description="Дата начала")
    end_date: str = Field(..., description="Дата окончания")
    days: List[DayPlan] = Field(..., description="Дневные маршруты")
    weather_info: List[WeatherInfo] = Field(default=[], description="Информация о погоде")
    overall_suggestions: str = Field(..., description="Общие рекомендации")
    budget: Optional[Budget] = Field(default=None, description="Бюджет")


class TripPlanResponse(BaseModel):
    """Ответ с планом путешествия"""
    success: bool = Field(..., description="Признак успеха")
    message: str = Field(default="", description="Сообщение")
    data: Optional[TripPlan] = Field(default=None, description="Данные плана путешествия")


class POIInfo(BaseModel):
    """Информация о POI"""
    id: str = Field(..., description="Идентификатор POI")
    name: str = Field(..., description="Название")
    type: str = Field(..., description="Тип")
    address: str = Field(..., description="Адрес")
    location: Location = Field(..., description="Координаты")
    tel: Optional[str] = Field(default=None, description="Телефон")


class POISearchResponse(BaseModel):
    """Ответ на поиск POI"""
    success: bool = Field(..., description="Признак успеха")
    message: str = Field(default="", description="Сообщение")
    data: List[POIInfo] = Field(default=[], description="Список POI")


class RouteInfo(BaseModel):
    """Информация о маршруте"""
    distance: float = Field(..., description="Расстояние (метры)")
    duration: int = Field(..., description="Время (секунды)")
    route_type: str = Field(..., description="Тип маршрута")
    description: str = Field(..., description="Описание маршрута")


class RouteResponse(BaseModel):
    """Ответ на запрос маршрута"""
    success: bool = Field(..., description="Признак успеха")
    message: str = Field(default="", description="Сообщение")
    data: Optional[RouteInfo] = Field(default=None, description="Информация о маршруте")


class WeatherResponse(BaseModel):
    """Ответ на запрос погоды"""
    success: bool = Field(..., description="Признак успеха")
    message: str = Field(default="", description="Сообщение")
    data: List[WeatherInfo] = Field(default=[], description="Информация о погоде")


# ============ Ответы с ошибками ============

class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    success: bool = Field(default=False, description="Признак успеха")
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(default=None, description="Код ошибки")
