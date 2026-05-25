# Кибер-городок — глобальная конфигурация
extends Node

# ==================== Настройки API ====================
const API_BASE_URL = "http://localhost:8000"
const API_CHAT = API_BASE_URL + "/chat"
const API_NPCS = API_BASE_URL + "/npcs"
const API_NPC_STATUS = API_BASE_URL + "/npcs/status"

# ==================== Настройки NPC ====================
const NPC_NAMES = ["Иван", "Пётр", "Сергей"]
const NPC_TITLES = {
	"Иван": "Python-инженер",
	"Пётр": "продакт-менеджер",
	"Сергей": "UI-дизайнер"
}

# ==================== Настройки игры ====================
const PLAYER_SPEED = 200.0  # Скорость передвижения игрока
const INTERACTION_DISTANCE = 80.0  # Дистанция взаимодействия
const NPC_STATUS_UPDATE_INTERVAL = 30.0  # Интервал обновления статусов NPC (сек)

# ==================== Настройки UI ====================
const DIALOGUE_FADE_TIME = 0.3  # Время плавного появления/скрытия окна диалога
const NPC_LABEL_OFFSET = Vector2(0, -60)  # Смещение надписи с именем NPC

# ==================== Настройки отладки ====================
const DEBUG_MODE = true  # Режим отладки
const SHOW_INTERACTION_RANGE = true  # Показывать радиус взаимодействия

# ==================== Утилитарные функции ====================
func log_info(message: String) -> void:
	if DEBUG_MODE:
		print("[INFO] ", message)

func log_error(message: String) -> void:
	print("[ERROR] ", message)

func log_api(endpoint: String, data: Dictionary) -> void:
	if DEBUG_MODE:
		print("[API] ", endpoint, " -> ", JSON.stringify(data))
