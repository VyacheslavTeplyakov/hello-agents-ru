"""Маршруты API для планирования путешествий"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["Планирование путешествий"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="Сформировать план путешествия",
    description="Формирование детального плана путешествия на основе запроса пользователя"
)
async def plan_trip(request: TripRequest):
    """
    Формирование плана путешествия

    Args:
        request: Параметры запроса на путешествие

    Returns:
        Ответ с планом путешествия
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 Получен запрос на планирование путешествия:")
        print(f"   Город: {request.city}")
        print(f"   Даты: {request.start_date} - {request.end_date}")
        print(f"   Дней: {request.travel_days}")
        print(f"{'='*60}\n")

        # Получаем экземпляр агента
        print("🔄 Получение экземпляра системы с несколькими агентами...")
        agent = get_trip_planner_agent()

        # Формируем план путешествия
        print("🚀 Начало формирования плана путешествия...")
        trip_plan = agent.plan_trip(request)

        print("✅ План путешествия сформирован успешно, подготовка ответа\n")

        return TripPlanResponse(
            success=True,
            message="План путешествия сформирован успешно",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ Ошибка формирования плана путешествия: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка формирования плана путешествия: {str(e)}"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности",
    description="Проверка доступности сервиса планирования путешествий"
)
async def health_check():
    """Проверка работоспособности"""
    try:
        # Проверяем доступность агента
        agent = get_trip_planner_agent()

        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис недоступен: {str(e)}"
        )
