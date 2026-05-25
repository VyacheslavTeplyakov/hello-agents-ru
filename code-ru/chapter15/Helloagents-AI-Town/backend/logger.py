"""Система логов диалогов"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Создаём директорию logs
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Формируем имя файла лога (по дате)
today = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOGS_DIR / f"dialogue_{today}.log"

# Формат логов
LOG_FORMAT = "%(asctime)s - %(message)s"
DATE_FORMAT = "%H:%M:%S"

# Создаём logger
dialogue_logger = logging.getLogger("dialogue")
dialogue_logger.setLevel(logging.INFO)

# Удаляем существующие handlers (чтобы избежать дублирования)
dialogue_logger.handlers.clear()

# Создаём файловый handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Создаём консольный handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Добавляем handlers
dialogue_logger.addHandler(file_handler)
dialogue_logger.addHandler(console_handler)

# Запрещаем передавать логи в root logger
dialogue_logger.propagate = False

def log_dialogue_start(npc_name: str, player_message: str):
    """Запись начала диалога"""
    dialogue_logger.info("=" * 60)
    dialogue_logger.info(f"💬 Начало диалога: {npc_name} <-> Игрок")
    dialogue_logger.info("=" * 60)
    dialogue_logger.info(f"📝 Сообщение игрока: {player_message}")

def log_affinity(npc_name: str, affinity: float, level: str):
    """Запись текущей симпатии"""
    dialogue_logger.info(f"💖 Текущая симпатия: {affinity:.1f}/100 ({level})")

def log_memory_retrieval(npc_name: str, count: int, memories: list = None):
    """Запись извлечения воспоминаний"""
    dialogue_logger.info(f"🧠 Найдено {count} релевантных воспоминаний")
    if memories:
        dialogue_logger.info("  📚 Релевантные воспоминания:")
        for i, mem in enumerate(memories[:3], 1):
            content = mem.content[:50] + "..." if len(mem.content) > 50 else mem.content
            dialogue_logger.info(f"    {i}. {content}")

def log_generating_response():
    """Запись начала генерации ответа"""
    dialogue_logger.info("🤖 Формирую ответ...")

def log_npc_response(npc_name: str, response: str):
    """Запись ответа NPC"""
    dialogue_logger.info(f"💬 Ответ {npc_name}: {response}")

def log_analyzing_affinity():
    """Запись начала анализа симпатии"""
    dialogue_logger.info("📊 Анализирую изменение симпатии...")

def log_affinity_change(affinity_result: dict):
    """Запись изменения симпатии"""
    if affinity_result.get("changed"):
        change_symbol = "📈" if affinity_result["change_amount"] > 0 else "📉"
        dialogue_logger.info(
            f"{change_symbol} Изменение симпатии: {affinity_result['old_affinity']:.1f} -> "
            f"{affinity_result['new_affinity']:.1f} ({affinity_result['change_amount']:+.1f})"
        )
        dialogue_logger.info(f"  Причина: {affinity_result['reason']}")
        dialogue_logger.info(f"  Эмоция: {affinity_result['sentiment']}")

        if affinity_result['old_level'] != affinity_result['new_level']:
            dialogue_logger.info(
                f"  🎉 Смена уровня отношений: {affinity_result['old_level']} -> {affinity_result['new_level']}"
            )
    else:
        dialogue_logger.info(f"  ➡️ Симпатия не изменилась (текущая: {affinity_result.get('affinity', 50.0):.1f})")
        dialogue_logger.info(f"  Причина: {affinity_result.get('reason', 'нет')}")

def log_memory_saved(npc_name: str):
    """Запись сохранения в память"""
    dialogue_logger.info(f"  💾 Диалог сохранён в памяти {npc_name}")

def log_dialogue_end():
    """Запись завершения диалога"""
    dialogue_logger.info("=" * 60)
    dialogue_logger.info("✅ Диалог завершён\n")

def log_info(message: str):
    """Запись обычного сообщения"""
    dialogue_logger.info(message)

def log_error(message: str):
    """Запись сообщения об ошибке"""
    dialogue_logger.error(message)

# При запуске показываем путь к файлу лога
print(f"\n📝 Файл логов диалогов: {LOG_FILE}")
print(f"📂 Директория логов: {LOGS_DIR}\n")
