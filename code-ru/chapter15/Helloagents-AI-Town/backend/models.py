"""Определения моделей данных"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Запрос диалога с одним NPC"""
    npc_name: str = Field(..., description="Имя NPC")
    message: str = Field(..., description="Сообщение игрока")

    class Config:
        json_schema_extra = {
            "example": {
                "npc_name": "Иван",
                "message": "Привет, чем ты занимаешься?"
            }
        }

class ChatResponse(BaseModel):
    """Ответ на диалог с одним NPC"""
    npc_name: str = Field(..., description="Имя NPC")
    npc_title: str = Field(..., description="Должность NPC")
    message: str = Field(..., description="Ответ NPC")
    success: bool = Field(default=True, description="Успешность выполнения")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Временная метка")

    class Config:
        json_schema_extra = {
            "example": {
                "npc_name": "Иван",
                "npc_title": "Python-инженер",
                "message": "Привет! Я как раз пишу код — дебажу мультиагентную систему.",
                "success": True
            }
        }

class NPCInfo(BaseModel):
    """Информация об NPC"""
    name: str = Field(..., description="Имя NPC")
    title: str = Field(..., description="Должность NPC")
    location: str = Field(..., description="Местоположение NPC")
    activity: str = Field(..., description="Текущее занятие")
    available: bool = Field(default=True, description="Доступен ли для диалога")

class NPCStatusResponse(BaseModel):
    """Ответ со статусом NPC"""
    dialogues: Dict[str, str] = Field(..., description="Текущие реплики NPC")
    last_update: Optional[datetime] = Field(None, description="Время последнего обновления")
    next_update_in: int = Field(..., description="Сколько секунд до следующего обновления")

    class Config:
        json_schema_extra = {
            "example": {
                "dialogues": {
                    "Иван": "Наконец-то починил этот баг, тесты проходят!",
                    "Пётр": "Надо подготовить материалы к продуктовому ревью на следующей неделе.",
                    "Сергей": "Цветовую палитру этого интерфейса ещё стоит подкорректировать."
                },
                "last_update": "2024-01-15T10:30:00",
                "next_update_in": 25
            }
        }

class NPCListResponse(BaseModel):
    """Ответ со списком NPC"""
    npcs: List[NPCInfo] = Field(..., description="Список NPC")
    total: int = Field(..., description="Общее число NPC")
