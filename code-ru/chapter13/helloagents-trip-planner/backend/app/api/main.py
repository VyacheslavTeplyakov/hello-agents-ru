"""Основное приложение FastAPI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import get_settings, validate_config, print_config
from .routes import trip, poi, map as map_routes

# Получаем конфигурацию
settings = get_settings()

# Создаём приложение FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API умного помощника по планированию путешествий на основе фреймворка HelloAgents",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем маршруты
app.include_router(trip.router, prefix="/api")
app.include_router(poi.router, prefix="/api")
app.include_router(map_routes.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    print("\n" + "="*60)
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print("="*60)

    # Печатаем информацию о конфигурации
    print_config()

    # Проверяем конфигурацию
    try:
        validate_config()
        print("\n✅ Конфигурация прошла проверку")
    except ValueError as e:
        print(f"\n❌ Ошибка проверки конфигурации:\n{e}")
        print("\nПроверьте файл .env и убедитесь, что все необходимые параметры настроены")
        raise

    print("\n" + "="*60)
    print("📚 Документация API: http://localhost:8000/docs")
    print("📖 ReDoc документация: http://localhost:8000/redoc")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Событие завершения приложения"""
    print("\n" + "="*60)
    print("👋 Приложение завершает работу...")
    print("="*60 + "\n")


@app.get("/")
async def root():
    """Корневой маршрут"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health():
    """Проверка работоспособности"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
