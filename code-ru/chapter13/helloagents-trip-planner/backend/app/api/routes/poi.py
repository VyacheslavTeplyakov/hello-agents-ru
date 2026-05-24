"""Маршруты API для работы с POI"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services.amap_service import get_amap_service
from ...services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel):
    """Ответ с деталями POI"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="Получить детали POI",
    description="Получение подробной информации об объекте POI по его идентификатору, включая фотографии"
)
async def get_poi_detail(poi_id: str):
    """
    Получение деталей POI

    Args:
        poi_id: Идентификатор POI

    Returns:
        Ответ с деталями POI
    """
    try:
        amap_service = get_amap_service()

        # Вызываем API деталей POI
        result = amap_service.get_poi_detail(poi_id)

        return POIDetailResponse(
            success=True,
            message="Детали POI получены успешно",
            data=result
        )

    except Exception as e:
        print(f"❌ Ошибка получения деталей POI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения деталей POI: {str(e)}"
        )


@router.get(
    "/search",
    summary="Поиск POI",
    description="Поиск объектов POI по ключевым словам"
)
async def search_poi(keywords: str, city: str = "Москва"):
    """
    Поиск POI

    Args:
        keywords: Ключевые слова для поиска
        city: Название города

    Returns:
        Результаты поиска
    """
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "Поиск выполнен успешно",
            "data": result
        }

    except Exception as e:
        print(f"❌ Ошибка поиска POI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка поиска POI: {str(e)}"
        )


@router.get(
    "/photo",
    summary="Получить фото достопримечательности",
    description="Получение фотографии достопримечательности из Unsplash по её названию"
)
async def get_attraction_photo(name: str):
    """
    Получение фото достопримечательности

    Args:
        name: Название достопримечательности

    Returns:
        URL фотографии
    """
    try:
        unsplash_service = get_unsplash_service()

        # Ищем фото достопримечательности
        photo_url = unsplash_service.get_photo_url(f"{name} Russia landmark")

        if not photo_url:
            # Если не нашли, пробуем только по названию
            photo_url = unsplash_service.get_photo_url(name)

        return {
            "success": True,
            "message": "Фото получено успешно",
            "data": {
                "name": name,
                "photo_url": photo_url
            }
        }

    except Exception as e:
        print(f"❌ Ошибка получения фото достопримечательности: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения фото достопримечательности: {str(e)}"
        )
