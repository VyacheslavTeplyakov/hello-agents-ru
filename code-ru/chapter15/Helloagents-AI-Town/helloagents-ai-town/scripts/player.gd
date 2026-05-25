# Скрипт управления игроком
extends CharacterBody2D

# Скорость движения
@export var speed: float = 200.0

# Текущий NPC, с которым можно взаимодействовать
var nearby_npc: Node = null

# Состояние взаимодействия (во время взаимодействия движение запрещено)
var is_interacting: bool = false

# Ссылки на узлы
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var camera: Camera2D = $Camera2D

# Ссылки на звуковые эффекты ⭐
@onready var interact_sound: AudioStreamPlayer = null  # Звук взаимодействия
@onready var running_sound: AudioStreamPlayer = null  # Звук ходьбы

# Состояние звука ходьбы ⭐
var is_playing_running_sound: bool = false

func _ready():
	# Добавляемся в группу player (важно! NPC по этой группе узнаёт игрока)
	add_to_group("player")

	# Получаем узлы звуков (опционально, отсутствие не вызывает ошибку) ⭐
	interact_sound = get_node_or_null("InteractSound")
	running_sound = get_node_or_null("RunningSound")

	if interact_sound:
		print("[INFO] Звук взаимодействия игрока включён")
	else:
		print("[WARN] У игрока нет узла InteractSound, звук взаимодействия отключён")

	if running_sound:
		print("[INFO] Звук ходьбы игрока включён")
	else:
		print("[WARN] У игрока нет узла RunningSound, звук ходьбы отключён")

	Config.log_info("Игрок инициализирован")
	# Включаем камеру
	camera.enabled = true
	# Запускаем анимацию по умолчанию
	if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
		animated_sprite.play("idle")

func _physics_process(_delta: float):
	# При взаимодействии движение запрещено
	if is_interacting:
		velocity = Vector2.ZERO
		move_and_slide()
		# Анимация idle
		if animated_sprite.sprite_frames != null and animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")
		# Останавливаем звук ходьбы ⭐
		stop_running_sound()
		return

	# Получаем направление ввода
	var input_direction = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")

	# Задаём скорость
	velocity = input_direction * speed

	# Двигаемся
	move_and_slide()

	# Обновляем анимацию и направление
	update_animation(input_direction)

	# Обновляем звук ходьбы ⭐
	update_running_sound(input_direction)

func update_animation(direction: Vector2):
	"""Обновление анимации персонажа (4 направления)"""
	if animated_sprite.sprite_frames == null:
		return

	# Запускаем анимацию по направлению движения
	if direction.length() > 0:
		# Движемся — определяем доминирующее направление
		if abs(direction.x) > abs(direction.y):
			# Движение по горизонтали
			if direction.x > 0:
				# Вправо
				if animated_sprite.sprite_frames.has_animation("walk_right"):
					animated_sprite.play("walk_right")
					animated_sprite.flip_h = false
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = false
			else:
				# Влево
				if animated_sprite.sprite_frames.has_animation("walk_left"):
					animated_sprite.play("walk_left")
					animated_sprite.flip_h = false
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
					animated_sprite.flip_h = true
		else:
			# Движение по вертикали
			if direction.y > 0:
				# Вниз
				if animated_sprite.sprite_frames.has_animation("walk_down"):
					animated_sprite.play("walk_down")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
			else:
				# Вверх
				if animated_sprite.sprite_frames.has_animation("walk_up"):
					animated_sprite.play("walk_up")
				elif animated_sprite.sprite_frames.has_animation("walk"):
					animated_sprite.play("walk")
	else:
		# Покой
		if animated_sprite.sprite_frames.has_animation("idle"):
			animated_sprite.play("idle")

func _input(event: InputEvent):
	# Клавиша E — взаимодействие с NPC
	# Проверка клавиши E (KEY_E = 69)
	if event is InputEventKey:
		if event.pressed and not event.echo:
			# Отладка: печать всех клавиш
			print("[DEBUG] Клавиша: ", event.keycode, " (E=69, Enter=4194309)")

			if event.keycode == KEY_E or event.keycode == KEY_ENTER or event.is_action_pressed("ui_accept"):
				print("[DEBUG] Нажата клавиша E, nearby_npc=", nearby_npc)
				if nearby_npc != null:
					interact_with_npc()
					print("[INFO] E вызвало взаимодействие")
				else:
					print("[WARN] Рядом нет NPC для взаимодействия")

func interact_with_npc():
	"""Взаимодействие с ближайшим NPC"""
	if nearby_npc != null:
		# Воспроизводим звук взаимодействия ⭐
		if interact_sound:
			interact_sound.play()

		Config.log_info("Взаимодействие с NPC: " + nearby_npc.npc_name)
		# Отправляем сигнал в группу диалоговой системы
		get_tree().call_group("dialogue_system", "start_dialogue", nearby_npc.npc_name)

func set_nearby_npc(npc: Node):
	"""Задать ближайшего NPC"""
	nearby_npc = npc
	if npc != null:
		print("[INFO] ✅ Вход в зону NPC: ", npc.npc_name)
		Config.log_info("Вход в зону NPC: " + npc.npc_name)
	else:
		print("[INFO] ❌ Выход из зоны NPC")
		Config.log_info("Выход из зоны NPC")

func get_nearby_npc() -> Node:
	"""Получить ближайшего NPC"""
	return nearby_npc

func set_interacting(interacting: bool):
	"""Установить состояние взаимодействия"""
	is_interacting = interacting
	if interacting:
		print("[INFO] 🔒 Игрок во взаимодействии, движение запрещено")
		# Останавливаем звук ходьбы ⭐
		stop_running_sound()
	else:
		print("[INFO] 🔓 Игрок вышел из взаимодействия, движение разрешено")

# ⭐ Обновление звука ходьбы
func update_running_sound(direction: Vector2):
	"""Обновление звука ходьбы"""
	if running_sound == null:
		return

	# Если идёт движение
	if direction.length() > 0:
		# Если звук ещё не играет — запускаем
		if not is_playing_running_sound:
			running_sound.play()
			is_playing_running_sound = true
			print("[INFO] 🎵 Звук ходьбы запущен")
	else:
		# Если остановились — останавливаем звук
		stop_running_sound()

# ⭐ Остановить звук ходьбы
func stop_running_sound():
	"""Остановить звук ходьбы"""
	if running_sound and is_playing_running_sound:
		running_sound.stop()
		is_playing_running_sound = false
		print("[INFO] 🔇 Звук ходьбы остановлен")
