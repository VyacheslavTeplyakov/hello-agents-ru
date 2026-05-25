# API-клиент — связь с FastAPI бэкендом
extends Node

# Определение сигналов
signal chat_response_received(npc_name: String, message: String)
signal chat_error(error_message: String)
signal npc_status_received(dialogues: Dictionary)
signal npc_list_received(npcs: Array)

# Узлы HTTP-запросов
var http_chat: HTTPRequest
var http_status: HTTPRequest
var http_npcs: HTTPRequest

func _ready():
	# Создаём узлы HTTP-запросов
	http_chat = HTTPRequest.new()
	http_status = HTTPRequest.new()
	http_npcs = HTTPRequest.new()

	add_child(http_chat)
	add_child(http_status)
	add_child(http_npcs)

	# Подключаем сигналы
	http_chat.request_completed.connect(_on_chat_request_completed)
	http_status.request_completed.connect(_on_status_request_completed)
	http_npcs.request_completed.connect(_on_npcs_request_completed)

	print("[INFO] API-клиент инициализирован")

# ==================== API диалога ====================
func send_chat(npc_name: String, message: String) -> void:
	"""Отправляет запрос диалога"""
	var data = {
		"npc_name": npc_name,
		"message": message
	}

	var json_string = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]

	print("[API] POST /chat -> ", data)

	var error = http_chat.request(
		Config.API_CHAT,
		headers,
		HTTPClient.METHOD_POST,
		json_string
	)

	if error != OK:
		print("[ERROR] Не удалось отправить запрос диалога: ", error)
		chat_error.emit("Сбой сетевого запроса")

func _on_chat_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Обрабатывает ответ диалога"""
	if response_code != 200:
		print("[ERROR] Сбой запроса диалога: HTTP ", response_code)
		chat_error.emit("Ошибка сервера: " + str(response_code))
		return

	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())

	if parse_result != OK:
		print("[ERROR] Не удалось разобрать ответ")
		chat_error.emit("Сбой разбора ответа")
		return

	var response = json.data

	if response.has("success") and response["success"]:
		var npc_name = response["npc_name"]
		var msg = response["message"]
		print("[INFO] Получен ответ NPC: ", npc_name, " -> ", msg)
		chat_response_received.emit(npc_name, msg)
	else:
		chat_error.emit("Сбой диалога")

# ==================== API статуса NPC ====================
func get_npc_status() -> void:
	"""Получает статус NPC"""
	# Проверяем, не идёт ли уже обработка запроса
	if http_status.get_http_client_status() != HTTPClient.STATUS_DISCONNECTED:
		print("[WARN] Запрос статуса NPC уже обрабатывается, пропускаем")
		return

	print("[API] GET /npcs/status")

	var error = http_status.request(Config.API_NPC_STATUS)

	if error != OK:
		print("[ERROR] Не удалось получить статус NPC: ", error)

func _on_status_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Обрабатывает ответ статуса NPC"""
	if response_code != 200:
		print("[ERROR] Сбой запроса статуса NPC: HTTP ", response_code)
		return

	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())

	if parse_result != OK:
		print("[ERROR] Не удалось разобрать статус NPC")
		return

	var response = json.data

	if response.has("dialogues"):
		var dialogues = response["dialogues"]
		print("[INFO] Получено обновление статуса NPC: ", dialogues.size(), " шт.")
		npc_status_received.emit(dialogues)

# ==================== API списка NPC ====================
func get_npc_list() -> void:
	"""Получает список NPC"""
	print("[API] GET /npcs")

	var error = http_npcs.request(Config.API_NPCS)

	if error != OK:
		print("[ERROR] Не удалось получить список NPC: ", error)

func _on_npcs_request_completed(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Обрабатывает ответ со списком NPC"""
	if response_code != 200:
		print("[ERROR] Сбой запроса списка NPC: HTTP ", response_code)
		return

	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())

	if parse_result != OK:
		print("[ERROR] Не удалось разобрать список NPC")
		return

	var response = json.data

	if response.has("npcs"):
		var npcs = response["npcs"]
		print("[INFO] Получен список NPC: ", npcs.size(), " шт.")
		npc_list_received.emit(npcs)
