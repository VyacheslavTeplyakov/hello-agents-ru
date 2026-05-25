"""Основное приложение FastAPI для кибер-городка"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from models import (
    ChatRequest, ChatResponse,
    NPCStatusResponse, NPCListResponse, NPCInfo
)
from agents import get_npc_manager
from state_manager import get_state_manager

# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    # При запуске
    print("\n" + "="*60)
    print("🎮 Бэкенд-сервис кибер-городка запускается...")
    print("="*60)

    # Проверяем конфигурацию
    settings.validate()

    # Инициализируем менеджер NPC
    npc_manager = get_npc_manager()

    # Инициализируем и запускаем менеджер состояний
    state_manager = get_state_manager(settings.NPC_UPDATE_INTERVAL)
    await state_manager.start()

    print("\n✅ Все сервисы запущены!")
    print(f"📡 Адрес API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 Документация API: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print("="*60 + "\n")

    yield

    # При остановке
    print("\n🛑 Останавливаю сервисы...")
    await state_manager.stop()
    print("✅ Сервисы остановлены\n")

# Создаём FastAPI-приложение
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Кибер-городок — система диалогов с ИИ-NPC на основе HelloAgents",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные экземпляры менеджеров
npc_manager = None
state_manager = None

def get_managers():
    """Возвращает экземпляры менеджеров"""
    global npc_manager, state_manager
    if npc_manager is None:
        npc_manager = get_npc_manager()
    if state_manager is None:
        state_manager = get_state_manager()
    return npc_manager, state_manager

# ==================== Маршруты API ====================

@app.get("/")
async def root():
    """Корневой путь — информация об API"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "features": ["Диалоги с ИИ", "Система памяти NPC", "Система симпатии", "Пакетное обновление состояний"],
        "endpoints": {
            "docs": "/docs",
            "chat": "/chat",
            "npcs": "/npcs",
            "npcs_status": "/npcs/status",
            "npc_memories": "/npcs/{npc_name}/memories",
            "npc_affinity": "/npcs/{npc_name}/affinity",
            "all_affinities": "/affinities"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "healthy", "timestamp": "now"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_npc(request: ChatRequest):
    """Эндпоинт диалога с NPC

    Игрок ведёт диалог с указанным NPC в реальном времени; обработкой
    занимается отдельный агент.
    """
    npc_mgr, _ = get_managers()

    # Проверяем, существует ли NPC
    npc_info = npc_mgr.get_npc_info(request.npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{request.npc_name}» не существует"
        )

    try:
        # Передаём сообщение агенту NPC
        response_text = npc_mgr.chat(request.npc_name, request.message)

        return ChatResponse(
            npc_name=request.npc_name,
            npc_title=npc_info["title"],
            message=response_text,
            success=True
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Сбой обработки диалога: {str(e)}"
        )

@app.get("/npcs", response_model=NPCListResponse)
async def list_npcs():
    """Возвращает список всех NPC"""
    npc_mgr, _ = get_managers()

    npcs_data = npc_mgr.get_all_npcs()
    npcs = [NPCInfo(**npc) for npc in npcs_data]

    return NPCListResponse(
        npcs=npcs,
        total=len(npcs)
    )

@app.get("/npcs/status", response_model=NPCStatusResponse)
async def get_npcs_status():
    """Возвращает текущее состояние всех NPC

    Возвращает пакетно сгенерированные реплики NPC для отображения их
    самостоятельного поведения.
    """
    _, state_mgr = get_managers()

    state = state_mgr.get_current_state()

    return NPCStatusResponse(
        dialogues=state["dialogues"],
        last_update=state["last_update"],
        next_update_in=state["next_update_in"]
    )

@app.post("/npcs/status/refresh")
async def refresh_npcs_status():
    """Принудительно обновляет состояния NPC

    Немедленно запускает пакетную генерацию диалогов.
    """
    _, state_mgr = get_managers()

    await state_mgr.force_update()
    state = state_mgr.get_current_state()

    return {
        "message": "Состояния NPC обновлены",
        "dialogues": state["dialogues"]
    }

@app.get("/npcs/{npc_name}")
async def get_npc_info(npc_name: str):
    """Возвращает подробную информацию об NPC"""
    npc_mgr, state_mgr = get_managers()

    npc_info = npc_mgr.get_npc_info(npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{npc_name}» не существует"
        )

    # Добавляем текущую реплику
    current_dialogue = state_mgr.get_npc_dialogue(npc_name)
    npc_info["current_dialogue"] = current_dialogue

    return npc_info

@app.get("/npcs/{npc_name}/memories")
async def get_npc_memories(npc_name: str, limit: int = 10):
    """Возвращает список воспоминаний NPC

    Args:
        npc_name: имя NPC
        limit: ограничение количества воспоминаний (по умолчанию 10)

    Returns:
        список воспоминаний NPC
    """
    npc_mgr, _ = get_managers()

    # Проверяем, существует ли NPC
    npc_info = npc_mgr.get_npc_info(npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{npc_name}» не существует"
        )

    try:
        memories = npc_mgr.get_npc_memories(npc_name, limit=limit)

        return {
            "npc_name": npc_name,
            "memories": memories,
            "total": len(memories)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить воспоминания: {str(e)}"
        )

@app.delete("/npcs/{npc_name}/memories")
async def clear_npc_memories(npc_name: str, memory_type: str = None):
    """Очищает память NPC (для тестов)

    Args:
        npc_name: имя NPC
        memory_type: тип памяти (working/episodic). Если не задан — очищает всю память

    Returns:
        результат операции
    """
    npc_mgr, _ = get_managers()

    # Проверяем, существует ли NPC
    npc_info = npc_mgr.get_npc_info(npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{npc_name}» не существует"
        )

    try:
        npc_mgr.clear_npc_memory(npc_name, memory_type)

        return {
            "message": f"Память {npc_name} очищена",
            "npc_name": npc_name,
            "memory_type": memory_type or "all"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось очистить память: {str(e)}"
        )

@app.get("/npcs/{npc_name}/affinity")
async def get_npc_affinity(npc_name: str, player_id: str = "player"):
    """Возвращает симпатию NPC к игроку

    Args:
        npc_name: имя NPC
        player_id: идентификатор игрока (по умолчанию «player»)

    Returns:
        информация о симпатии
    """
    npc_mgr, _ = get_managers()

    # Проверяем, существует ли NPC
    npc_info = npc_mgr.get_npc_info(npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{npc_name}» не существует"
        )

    try:
        affinity_info = npc_mgr.get_npc_affinity(npc_name, player_id)

        return {
            "npc_name": npc_name,
            "player_id": player_id,
            **affinity_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить симпатию: {str(e)}"
        )

@app.get("/affinities")
async def get_all_affinities(player_id: str = "player"):
    """Возвращает симпатию всех NPC к игроку

    Args:
        player_id: идентификатор игрока (по умолчанию «player»)

    Returns:
        информация о симпатии всех NPC
    """
    npc_mgr, _ = get_managers()

    try:
        affinities = npc_mgr.get_all_affinities(player_id)

        return {
            "player_id": player_id,
            "affinities": affinities
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить симпатии: {str(e)}"
        )

@app.put("/npcs/{npc_name}/affinity")
async def set_npc_affinity(npc_name: str, affinity: float, player_id: str = "player"):
    """Устанавливает симпатию NPC к игроку (для тестов)

    Args:
        npc_name: имя NPC
        affinity: значение симпатии (0-100)
        player_id: идентификатор игрока (по умолчанию «player»)

    Returns:
        результат операции
    """
    npc_mgr, _ = get_managers()

    # Проверяем, существует ли NPC
    npc_info = npc_mgr.get_npc_info(npc_name)
    if not npc_info:
        raise HTTPException(
            status_code=404,
            detail=f"NPC «{npc_name}» не существует"
        )

    # Проверяем диапазон симпатии
    if affinity < 0 or affinity > 100:
        raise HTTPException(
            status_code=400,
            detail="Симпатия должна быть в диапазоне 0-100"
        )

    try:
        npc_mgr.set_npc_affinity(npc_name, affinity, player_id)
        affinity_info = npc_mgr.get_npc_affinity(npc_name, player_id)

        return {
            "message": f"Симпатия {npc_name} к игроку установлена",
            "npc_name": npc_name,
            "player_id": player_id,
            **affinity_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось установить симпатию: {str(e)}"
        )

# ==================== Точка входа ====================

if __name__ == "__main__":
    print("\n🚀 Запускаю бэкенд-сервис кибер-городка...")
    print(f"📍 Адрес прослушивания: {settings.API_HOST}:{settings.API_PORT}")
    print(f"📖 Документация: http://localhost:{settings.API_PORT}/docs\n")

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,  # Автоперезагрузка в режиме разработки
        log_level="info"
    )
