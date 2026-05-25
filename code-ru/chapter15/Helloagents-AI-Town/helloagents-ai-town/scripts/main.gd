# Скрипт главной сцены
extends Node2D

# Ссылки на узлы NPC
@onready var npc_zhang: Node2D = $NPCs/NPC_Zhang
@onready var npc_li: Node2D = $NPCs/NPC_Li
@onready var npc_wang: Node2D = $NPCs/NPC_Wang

# API-клиент
var api_client: Node = null

# Таймер обновления статусов NPC
var status_update_timer: float = 0.0

func _ready():
	print("[INFO] Главная сцена инициализирована")

	# Получаем API-клиент
	api_client = get_node_or_null("/root/APIClient")
	if api_client:
		api_client.npc_status_received.connect(_on_npc_status_received)

		# Сразу запрашиваем статус NPC
		api_client.get_npc_status()
	else:
		print("[ERROR] API-клиент не найден")

func _process(delta: float):
	# Периодически обновляем статусы NPC
	status_update_timer += delta
	if status_update_timer >= Config.NPC_STATUS_UPDATE_INTERVAL:
		status_update_timer = 0.0
		if api_client:
			api_client.get_npc_status()

func _on_npc_status_received(dialogues: Dictionary):
	"""Получено обновление статусов NPC"""
	print("[INFO] Обновляю статусы NPC: ", dialogues)

	# Обновляем реплики всех NPC
	for npc_name in dialogues:
		var dialogue = dialogues[npc_name]
		update_npc_dialogue(npc_name, dialogue)

func update_npc_dialogue(npc_name: String, dialogue: String):
	"""Обновить реплику указанного NPC"""
	var npc_node = get_npc_node(npc_name)
	if npc_node and npc_node.has_method("update_dialogue"):
		npc_node.update_dialogue(dialogue)

func get_npc_node(npc_name: String) -> Node2D:
	"""Получить узел NPC по имени"""
	match npc_name:
		"Иван":
			return npc_zhang
		"Пётр":
			return npc_li
		"Сергей":
			return npc_wang
		_:
			return null
