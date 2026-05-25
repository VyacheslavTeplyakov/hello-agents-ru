# Скрипт NPC
extends CharacterBody2D  # ⭐ Изменили на CharacterBody2D

# Информация о NPC
@export var npc_name: String = "Иван"
@export var npc_title: String = "Python-инженер"

# Настройка внешнего вида NPC
@export var sprite_frames: SpriteFrames = null  # Кастомный ресурс кадров спрайта

# Настройки передвижения NPC ⭐
@export var move_speed: float = 50.0  # Скорость передвижения
@export var wander_enabled: bool = true  # Включить блуждание
@export var wander_range: float = 200.0  # Радиус блуждания
@export var wander_interval_min: float = 3.0  # Минимальный интервал блуждания (сек)
@export var wander_interval_max: float = 8.0  # Максимальный интервал блуждания (сек)

# Текущая реплика (получена от бэкенда)
var current_dialogue: String = ""

# Ссылки на узлы
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var interaction_area: Area2D = $InteractionArea
@onready var name_label: Label = $NameLabel
@onready var dialogue_label: Label = $DialogueLabel

# Подсказка о взаимодействии (опциональный узел, отсутствие не вызывает ошибку)
var interaction_hint: Label = null

# Ссылка на игрока
var player: Node = null

# Переменные блуждания ⭐
var wander_target: Vector2 = Vector2.ZERO  # Цель блуждания
var wander_timer: float = 0.0  # Таймер блуждания
var is_wandering: bool = false  # Идёт ли блуждание
var is_interacting: bool = false  # Идёт ли взаимодействие с игроком
var spawn_position: Vector2 = Vector2.ZERO  # Начальная позиция

func _ready():
	# Добавляемся в группу npcs ⭐
	add_to_group("npcs")

	# Задаём имя NPC
	name_label.text = npc_name

	# Подключаем сигналы зоны взаимодействия
	interaction_area.body_entered.connect(_on_body_entered)
	interaction_area.body_exited.connect(_on_body_exited)

	# Инициализируем метку реплики
	dialogue_label.text = ""
	dialogue_label.visible = false

	# Пытаемся получить узел подсказки взаимодействия (опционально)
	interaction_hint = get_node_or_null("InteractionHint")
	if interaction_hint:
		interaction_hint.text = "Нажмите E для взаимодействия"
		interaction_hint.visible = false
		print("[INFO] Подсказка взаимодействия NPC включена: ", npc_name)
	else:
		print("[WARN] У NPC нет узла InteractionHint, подсказка отключена: ", npc_name)

	# Применяем кастомные кадры спрайта (если заданы)
	if sprite_frames != null:
		animated_sprite.sprite_frames = sprite_frames
		print("[INFO] NPC использует кастомный спрайт: ", npc_name)

	# Запускаем анимацию по умолчанию
	if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
		animated_sprite.play("idle")

	# Запоминаем начальную позицию ⭐
	spawn_position = global_position

	# Инициализируем таймер блуждания ⭐
	if wander_enabled:
		wander_timer = randf_range(wander_interval_min, wander_interval_max)
		choose_new_wander_target()

	Config.log_info("Инициализирован NPC: " + npc_name)

func _on_body_entered(body: Node2D):
	"""Игрок входит в зону взаимодействия"""
	print("[DEBUG] NPC ", npc_name, " зафиксировал вход объекта: ", body.name, ", в группе player: ", body.is_in_group("player"))

	if body.is_in_group("player"):
		player = body
		print("[INFO] ✅ Игрок вошёл в зону NPC: ", npc_name)

		if player.has_method("set_nearby_npc"):
			player.set_nearby_npc(self)
		else:
			print("[ERROR] У игрока нет метода set_nearby_npc!")

		# Показываем подсказку
		show_interaction_hint()

func _on_body_exited(body: Node2D):
	"""Игрок выходит из зоны взаимодействия"""
	print("[DEBUG] NPC ", npc_name, " зафиксировал выход объекта: ", body.name)

	if body.is_in_group("player"):
		print("[INFO] ❌ Игрок покинул зону NPC: ", npc_name)

		if player != null and player.has_method("set_nearby_npc"):
			player.set_nearby_npc(null)
		player = null

		# Скрываем подсказку
		hide_interaction_hint()

func show_interaction_hint():
	"""Показать подсказку взаимодействия"""
	if interaction_hint:
		interaction_hint.visible = true
		print("[INFO] Подсказка показана: ", npc_name)

func hide_interaction_hint():
	"""Скрыть подсказку взаимодействия"""
	if interaction_hint:
		interaction_hint.visible = false
		print("[INFO] Подсказка скрыта: ", npc_name)

func update_dialogue(dialogue: String):
	"""Обновить реплику NPC"""
	current_dialogue = dialogue
	dialogue_label.text = dialogue
	dialogue_label.visible = true

	# Скрываем реплику через 10 секунд (увеличено время показа)
	await get_tree().create_timer(10.0).timeout
	dialogue_label.visible = false

func get_npc_name() -> String:
	return npc_name

func get_npc_title() -> String:
	return npc_title

# ⭐ Физическое обновление — обработка движения
func _physics_process(delta: float):
	"""Физическое обновление — обработка движения"""
	# Если идёт взаимодействие с игроком — останавливаемся
	if is_interacting:
		velocity = Vector2.ZERO
		move_and_slide()
		# Включаем анимацию idle
		if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")
		return

	# Если блуждание выключено — не двигаемся
	if not wander_enabled:
		return

	# Обновляем таймер блуждания
	wander_timer -= delta

	# Если таймер истёк — выбираем новую цель и идём
	if wander_timer <= 0:
		choose_new_wander_target()
		wander_timer = randf_range(wander_interval_min, wander_interval_max)

	# Если идёт блуждание — двигаемся к цели
	if is_wandering:
		# Проверяем достижение цели
		if global_position.distance_to(wander_target) < 10:
			# Цель достигнута — останавливаемся
			is_wandering = false
			velocity = Vector2.ZERO
			move_and_slide()
			# Анимация idle
			if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
				animated_sprite.play("idle")
		else:
			# Продолжаем движение к цели
			var direction = (wander_target - global_position).normalized()
			velocity = direction * move_speed
			move_and_slide()
			# Обновляем анимацию
			update_animation(direction)
	else:
		# Стоим на месте
		velocity = Vector2.ZERO
		move_and_slide()
		# Анимация idle
		if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")

# ⭐ Выбрать новую цель блуждания
func choose_new_wander_target():
	"""Выбрать новую цель блуждания"""
	# Выбираем случайную точку рядом с начальной позицией
	var offset = Vector2(
		randf_range(-wander_range, wander_range),
		randf_range(-wander_range, wander_range)
	)
	wander_target = spawn_position + offset
	is_wandering = true

	Config.log_info("NPC %s выбрал новую цель: %s" % [npc_name, wander_target])

# ⭐ Обновление анимации
func update_animation(direction: Vector2):
	"""Обновление анимации"""
	if animated_sprite.sprite_frames == null:
		return

	if direction.length() > 0:
		# Анимация движения
		if abs(direction.x) > abs(direction.y):
			# Движение влево/вправо
			if direction.x > 0:
				if animated_sprite.sprite_frames.has_animation("walk_right"):
					animated_sprite.play("walk_right")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = false
			else:
				if animated_sprite.sprite_frames.has_animation("walk_left"):
					animated_sprite.play("walk_left")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = true
		else:
			# Движение вверх/вниз
			if direction.y > 0:
				if animated_sprite.sprite_frames.has_animation("walk_down"):
					animated_sprite.play("walk_down")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
			else:
				if animated_sprite.sprite_frames.has_animation("walk_up"):
					animated_sprite.play("walk_up")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
	else:
		# Анимация покоя
		if animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")

# ⭐ Установить состояние взаимодействия
func set_interacting(interacting: bool):
	"""Установить состояние взаимодействия"""
	is_interacting = interacting
	if interacting:
		Config.log_info("NPC %s входит во взаимодействие, движение остановлено" % npc_name)
	else:
		Config.log_info("NPC %s выходит из взаимодействия, движение возобновлено" % npc_name)
