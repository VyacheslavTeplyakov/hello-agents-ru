"""Маршруты API картографического сервиса"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ...models.schemas import (
    POISearchRequest,
    POISearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherResponse
)
from ...services.amap_service import get_amap_service

router = APIRouter(prefix="/map", tags=["Картографический сервис"])


@router.get(
    "/poi",
    response_model=POISearchResponse,
    summary="Поиск POI",
    description="Поиск объектов POI (точек интереса) по ключевым словам"
)
async def search_poi(
    keywords: str = Query(..., description="Ключевые слова для поиска", example="Кремль"),
    city: str = Query(..., description="Город", example="Москва"),
    citylimit: bool = Query(True, description="Ограничить поиск пределами города")
):
    """
    Поиск POI

    Args:
        keywords: Ключевые слова для поиска
        city: Город
        citylimit: Ограничить поиск пределами города

    Returns:
        Результаты поиска POI
    """
    try:
        # Получаем экземпляр сервиса
        service = get_amap_service()

        # Ищем POI
        pois = service.search_poi(keywords, city, citylimit)

        return POISearchResponse(
            success=True,
            message="Поиск POI выполнен успешно",
            data=pois
        )

    except Exception as e:
        print(f"❌ Ошибка поиска POI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка поиска POI: {str(e)}"
        )


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="Запрос погоды",
    description="Запрос информации о погоде в указанном городе"
)
async def get_weather(
    city: str = Query(..., description="Название города", example="Москва")
):
    """
    Запрос погоды

    Args:
        city: Название города

    Returns:
        Информация о погоде
    """
    try:
        # Получаем экземпляр сервиса
        service = get_amap_service()

        # Запрашиваем погоду
        weather_info = service.get_weather(city)

        return WeatherResponse(
            success=True,
            message="Запрос погоды выполнен успешно",
            data=weather_info
        )

    except Exception as e:
        print(f"❌ Ошибка запроса погоды: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запроса погоды: {str(e)}"
        )


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="Построение маршрута",
    description="Построение маршрута между двумя точками"
)
async def plan_route(request: RouteRequest):
    """
    Построение маршрута

    Args:
        request: Запрос на построение маршрута

    Returns:
        Информация о маршруте
    """
    try:
        # Получаем экземпляр сервиса
        service = get_amap_service()

        # Строим маршрут
        route_info = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )

        return RouteResponse(
            success=True,
            message="Маршрут построен успешно",
            data=route_info
        )

    except Exception as e:
        print(f"❌ Ошибка построения маршрута: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка построения маршрута: {str(e)}"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности",
    description="Проверка доступности картографического сервиса"
)
async def health_check():
    """Проверка работоспособности"""
    try:
        # Проверяем доступность сервиса
        service = get_amap_service()

        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_tools_count": len(service.mcp_tool._available_tools)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис недоступен: {str(e)}"
        )
