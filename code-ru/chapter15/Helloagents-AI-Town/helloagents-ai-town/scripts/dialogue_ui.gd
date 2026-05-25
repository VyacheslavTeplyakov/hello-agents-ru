# Скрипт UI диалога
extends CanvasLayer

# Ссылки на узлы
@onready var panel: Panel = $Panel
@onready var npc_name_label: Label = $Panel/NPCName
@onready var npc_title_label: Label = $Panel/NPCTitle
@onready var dialogue_text: RichTextLabel = $Panel/DialogueText
@onready var player_input: LineEdit = $Panel/PlayerInput
@onready var send_button: Button = $Panel/SendButton
@onready var close_button: Button = $Panel/CloseButton

# Текущий собеседник-NPC
var current_npc_name: String = ""

# Ссылка на API-клиент
var api_client: Node = null

func _ready():
	# Добавляемся в группу диалоговой системы
	add_to_group("dialogue_system")

	# Изначально скрыто
	visible = false

	# Подключаем сигналы кнопок
	send_button.pressed.connect(_on_send_button_pressed)
	close_button.pressed.connect(_on_close_button_pressed)
	player_input.text_submitted.connect(_on_text_submitted)

	# Получаем API-клиент
	api_client = get_node_or_null("/root/APIClient")
	if api_client:
		api_client.chat_response_received.connect(_on_chat_response_received)
		api_client.chat_error.connect(_on_chat_error)

	print("[INFO] UI диалога инициализирован")

# ⭐ Обработка горячих клавиш окна диалога
func _input(event: InputEvent):
	# Если окно скрыто — не обрабатываем
	if not visible:
		return

	if event is InputEventKey and event.pressed and not event.echo:
		# Клавиша ESC — закрыть окно диалога
		if event.keycode == KEY_ESCAPE:
			hide_dialogue()
			get_viewport().set_input_as_handled()
			print("[DEBUG] ESC: окно диалога закрыто")
			return

		# Клавиша Enter — отправить сообщение (только когда поле ввода в фокусе)
		# Замечание: сигнал text_submitted у LineEdit уже обрабатывает Enter, это запасной вариант
		if event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:
			# Если поле ввода в фокусе, пусть LineEdit обработает сам
			if player_input.has_focus():
				return
			# Иначе отправляем вручную
			send_message()
			get_viewport().set_input_as_handled()
			print("[DEBUG] Enter: сообщение отправлено")
			return

		# Блокируем клавиши движения и взаимодействия, чтобы не вызвать игровые действия ⭐ WASD
		if event.keycode in [KEY_E, KEY_SPACE, KEY_W, KEY_A, KEY_S, KEY_D]:
			get_viewport().set_input_as_handled()
			# Печатаем только при первой блокировке, чтобы не флудить
			match event.keycode:
				KEY_E:
					print("[DEBUG] В окне диалога заблокирована клавиша E")
				KEY_SPACE:
					print("[DEBUG] В окне диалога заблокирован пробел")
				KEY_W:
					print("[DEBUG] В окне диалога заблокирована клавиша W")
				KEY_A:
					print("[DEBUG] В окне диалога заблокирована клавиша A")
				KEY_S:
					print("[DEBUG] В окне диалога заблокирована клавиша S")
				KEY_D:
					print("[DEBUG] В окне диалога заблокирована клавиша D")

func start_dialogue(npc_name: String):
	"""Начать диалог с NPC"""
	current_npc_name = npc_name

	# Уведомляем NPC о входе во взаимодействие (остановить движение)
	var npc = get_npc_by_name(npc_name)
	if npc and npc.has_method("set_interacting"):
		npc.set_interacting(true)

	# Заполняем информацию о NPC
	npc_name_label.text = npc_name
	npc_title_label.text = Config.NPC_TITLES.get(npc_name, "")

	# Очищаем содержимое диалога
	dialogue_text.clear()
	dialogue_text.append_text("[color=gray]Начат диалог с " + npc_name + "...[/color]\n")

	# Очищаем поле ввода
	player_input.text = ""

	# Показываем окно диалога
	show_dialogue()

	# Передаём фокус полю ввода
	player_input.grab_focus()

	print("[INFO] Начат диалог: ", npc_name)

func show_dialogue():
	"""Показать окно диалога"""
	visible = true

	# Уведомляем игрока о входе во взаимодействие (запретить движение)
	var player = get_tree().get_first_node_in_group("player")
	if player and player.has_method("set_interacting"):
		player.set_interacting(true)

func hide_dialogue():
	"""Скрыть окно диалога"""
	visible = false

	# Уведомляем NPC об окончании взаимодействия (возобновить движение)
	if current_npc_name != "":
		var npc = get_npc_by_name(current_npc_name)
		if npc and npc.has_method("set_interacting"):
			npc.set_interacting(false)

	current_npc_name = ""

	# Уведомляем игрока об окончании взаимодействия (разрешить движение)
	var player = get_tree().get_first_node_in_group("player")
	if player and player.has_method("set_interacting"):
		player.set_interacting(false)

func _on_send_button_pressed():
	"""Нажатие кнопки отправки"""
	send_message()

func _on_text_submitted(_text: String):
	"""Enter в поле ввода"""
	send_message()

func send_message():
	"""Отправить сообщение"""
	var message = player_input.text.strip_edges()

	if message.is_empty():
		return

	if current_npc_name.is_empty():
		print("[ERROR] NPC не выбран")
		return

	# Показываем сообщение игрока
	dialogue_text.append_text("\n[color=cyan]Игрок:[/color] " + message + "\n")

	# Очищаем поле ввода
	player_input.text = ""

	# Показываем индикатор ожидания
	dialogue_text.append_text("[color=gray]Ожидание ответа...[/color]\n")

	# Отправляем запрос API
	if api_client:
		api_client.send_chat(current_npc_name, message)
	else:
		print("[ERROR] API-клиент не найден")

func _on_chat_response_received(npc_name: String, message: String):
	"""Получен ответ NPC"""
	if npc_name != current_npc_name:
		return

	# Убираем «Ожидание ответа...»
	var text = dialogue_text.get_parsed_text()
	if text.ends_with("Ожидание ответа...\n"):
		# Удаляем последнюю строку
		dialogue_text.clear()
		var lines = text.split("\n")
		for i in range(lines.size() - 2):
			dialogue_text.append_text(lines[i] + "\n")

	# Показываем ответ NPC
	dialogue_text.append_text("[color=yellow]" + npc_name + ":[/color] " + message + "\n")

	# Прокручиваем вниз
	dialogue_text.scroll_to_line(dialogue_text.get_line_count() - 1)

func _on_chat_error(error_message: String):
	"""Ошибка диалога"""
	dialogue_text.append_text("[color=red]Ошибка: " + error_message + "[/color]\n")

func _on_close_button_pressed():
	"""Нажатие кнопки закрытия"""
	hide_dialogue()

# ⭐ Получить узел NPC по имени
func get_npc_by_name(npc_name: String) -> Node:
	"""Получить узел NPC по имени"""
	var npcs = get_tree().get_nodes_in_group("npcs")
	for npc in npcs:
		if npc.npc_name == npc_name:
			return npc
	return null
