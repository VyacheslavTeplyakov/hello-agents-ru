"""Менеджер состояний NPC — периодически пакетно обновляет диалоги NPC"""

import asyncio
from datetime import datetime
from typing import Dict, Optional
from batch_generator import get_batch_generator

class NPCStateManager:
    """Менеджер состояний NPC

    Функции:
    1. Периодическая пакетная генерация диалогов (для снижения стоимости API)
    2. Кэширование текущих состояний NPC
    3. Предоставление эндпоинтов для запроса состояния
    """

    def __init__(self, update_interval: int = 30):
        """Инициализирует менеджер состояний

        Args:
            update_interval: интервал обновления в секундах (по умолчанию 30)
        """
        self.update_interval = update_interval
        self.batch_generator = get_batch_generator()

        # Текущее состояние
        self.current_dialogues: Dict[str, str] = {}
        self.last_update: Optional[datetime] = None
        self.next_update_time: Optional[datetime] = None

        # Фоновая задача
        self._update_task: Optional[asyncio.Task] = None
        self._running = False

        print(f"📊 Менеджер состояний NPC инициализирован (интервал обновления: {update_interval} сек)")

    async def start(self):
        """Запускает фоновую задачу обновления"""
        if self._running:
            print("⚠️  Менеджер состояний уже работает")
            return

        self._running = True
        print("🚀 Запускаю автоматическое обновление состояний NPC...")

        # Сразу выполняем одно обновление
        await self._update_npc_states()

        # Запускаем цикл периодических обновлений
        self._update_task = asyncio.create_task(self._auto_update_loop())

    async def stop(self):
        """Останавливает фоновую задачу обновления"""
        if not self._running:
            return

        self._running = False

        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        print("🛑 Автоматическое обновление состояний NPC остановлено")

    async def _auto_update_loop(self):
        """Цикл автоматических обновлений"""
        while self._running:
            try:
                await asyncio.sleep(self.update_interval)
                await self._update_npc_states()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Сбой автоматического обновления: {e}")
                # Продолжаем работу, не прерываемся

    async def _update_npc_states(self):
        """Обновляет состояния NPC"""
        try:
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Запускаю пакетное обновление диалогов NPC...")

            # Пакетно генерируем диалоги
            new_dialogues = self.batch_generator.generate_batch_dialogues()

            # Обновляем состояние
            self.current_dialogues = new_dialogues
            self.last_update = datetime.now()
            self.next_update_time = datetime.now()

            # Выводим результат обновления
            print("📝 Диалоги NPC обновлены:")
            for npc_name, dialogue in new_dialogues.items():
                print(f"   - {npc_name}: {dialogue}")

        except Exception as e:
            print(f"❌ Не удалось обновить состояния NPC: {e}")

    def get_current_state(self) -> Dict:
        """Возвращает текущее состояние"""
        # Считаем, сколько осталось до следующего обновления
        if self.last_update:
            elapsed = (datetime.now() - self.last_update).total_seconds()
            next_update_in = max(0, int(self.update_interval - elapsed))
        else:
            next_update_in = self.update_interval

        return {
            "dialogues": self.current_dialogues,
            "last_update": self.last_update,
            "next_update_in": next_update_in
        }

    def get_npc_dialogue(self, npc_name: str) -> Optional[str]:
        """Возвращает текущую реплику указанного NPC"""
        return self.current_dialogues.get(npc_name)

    async def force_update(self):
        """Принудительно запускает обновление прямо сейчас"""
        print("⚡ Принудительно обновляю состояния NPC...")
        await self._update_npc_states()

# Глобальный экземпляр-синглтон
_state_manager = None

def get_state_manager(update_interval: int = 30) -> NPCStateManager:
    """Возвращает singleton-экземпляр менеджера состояний"""
    global _state_manager
    if _state_manager is None:
        _state_manager = NPCStateManager(update_interval)
    return _state_manager
