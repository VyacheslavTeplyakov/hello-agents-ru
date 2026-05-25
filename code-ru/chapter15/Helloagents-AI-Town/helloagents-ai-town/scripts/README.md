# Кибер-городок — описание GDScript-скриптов

## Список файлов скриптов

```
scripts/
├── config.gd          # Глобальная конфигурация
├── api_client.gd      # Клиент для общения с API
├── player.gd          # Управление игроком
├── npc.gd             # Поведение NPC
├── dialogue_ui.gd     # UI диалога
└── main.gd            # Логика главной сцены
```

---

## Подробно по скриптам

### 1. config.gd (глобальная конфигурация)
**Назначение:** хранит глобальные константы и настройки.

**Ключевые параметры:**
```gdscript
const API_BASE_URL = "http://localhost:8000"  # Адрес бэкенда
const PLAYER_SPEED = 200.0                     # Скорость игрока
const NPC_STATUS_UPDATE_INTERVAL = 30.0        # Интервал обновления NPC
```

**Использование:**
```gdscript
# Доступ из любого скрипта
Config.log_info("сообщение")
var speed = Config.PLAYER_SPEED
```

---

### 2. api_client.gd (API-клиент)
**Назначение:** связь с FastAPI-бэкендом.

**Основные методы:**
- `send_chat(npc_name, message)` — отправить сообщение
- `get_npc_status()` — получить статус NPC
- `get_npc_list()` — получить список NPC

**Сигналы:**
- `chat_response_received(npc_name, message)` — получен ответ
- `chat_error(error_message)` — ошибка диалога
- `npc_status_received(dialogues)` — получены статусы

**Пример использования:**
```gdscript
# Получаем API-клиент
var api = get_node("/root/APIClient")

# Отправляем сообщение
api.send_chat("Иван", "Привет")

# Подписываемся на ответ
api.chat_response_received.connect(_on_response)

func _on_response(npc_name, message):
    print(npc_name + ": " + message)
```

---

### 3. player.gd (управление игроком)
**Назначение:** обрабатывает передвижение и взаимодействие игрока.

**Ключевой функционал:**
- Движение WASD / стрелками
- Клавиша E — взаимодействие с NPC
- Определение ближайших NPC

**Требуемые узлы:**
```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
└── Camera2D
```

**Параметры:**
```gdscript
@export var speed: float = 200.0  # Настраивается в инспекторе
```

---

### 4. npc.gd (поведение NPC)
**Назначение:** взаимодействие NPC с игроком и отображение состояния.

**Ключевой функционал:**
- Отслеживание входа/выхода игрока в зону взаимодействия
- Отображение имени и реплики NPC
- Обновление состояния NPC

**Требуемые узлы:**
```
NPC (Node2D)
├── Sprite2D
├── InteractionArea (Area2D)
│   └── CollisionShape2D
├── NameLabel (Label)
└── DialogueLabel (Label)
```

**Экспортируемые параметры:**
```gdscript
@export var npc_name: String = "Иван"
@export var npc_title: String = "Python-инженер"
```

**Использование:**
1. Задайте имя и должность NPC в инспекторе
2. Скрипт сам обрабатывает логику взаимодействия

---

### 5. dialogue_ui.gd (UI диалога)
**Назначение:** управление интерфейсом диалога.

**Ключевой функционал:**
- Показ и скрытие окна диалога
- Обработка ввода игрока
- Отображение истории диалога
- Связь с API

**Требуемые узлы:**
```
DialogueUI (CanvasLayer)
└── Panel
    ├── NPCName (Label)
    ├── NPCTitle (Label)
    ├── DialogueText (RichTextLabel)
    ├── PlayerInput (LineEdit)
    ├── SendButton (Button)
    └── CloseButton (Button)
```

**Использование:**
```gdscript
# Начать диалог
get_tree().call_group("dialogue_system", "start_dialogue", "Иван")
```

---

### 6. main.gd (главная сцена)
**Назначение:** управление всей сценой игры.

**Ключевой функционал:**
- Периодическое обновление статусов NPC
- Распределение реплик по узлам NPC
- Координация подсистем

**Требуемые узлы:**
```
Main (Node2D)
├── TileMapLayer (карта)
├── Player (экземпляр)
├── NPCs (Node2D)
│   ├── NPC_Zhang (экземпляр)
│   ├── NPC_Li (экземпляр)
│   └── NPC_Wang (экземпляр)
└── DialogueUI (экземпляр)
```

---

## Как использовать скрипты

### Шаг 1. Настройка AutoLoad
В `Project -> Project Settings -> AutoLoad` добавьте:
- `config.gd` -> имя: `Config`
- `api_client.gd` -> имя: `APIClient`

### Шаг 2. Прикрепите скрипты к сценам
- `player.tscn` -> `player.gd`
- `npc.tscn` -> `npc.gd`
- `dialogue_ui.tscn` -> `dialogue_ui.gd`
- `main.tscn` -> `main.gd`

### Шаг 3. Настройте узлы
Убедитесь, что структура узлов каждой сцены соответствует требованиям скрипта.

### Шаг 4. Настройте параметры
В инспекторе задайте экспортируемые параметры (имя NPC, скорость и т.п.).

---

## Советы по отладке

### Просмотр логов
Все скрипты выводят логи через `Config.log_info()`, смотрите в панели **Output** в Godot.

### Типичные логи:
```
[INFO] API-клиент инициализирован
[INFO] Игрок инициализирован
[INFO] Инициализирован NPC: Иван
[INFO] Вход в зону NPC: Иван
[API] POST /chat -> {"npc_name":"Иван","message":"Привет"}
[INFO] Получен ответ NPC: Иван -> Привет! Я Python-инженер...
```

### Включение режима отладки
В `config.gd`:
```gdscript
const DEBUG_MODE = true  # Выводить подробные логи
const SHOW_INTERACTION_RANGE = true  # Показывать радиус взаимодействия
```

---

## Схема потока сигналов

```
Игрок нажимает E
    ↓
player.gd: interact_with_npc()
    ↓
Сигнал группе dialogue_system
    ↓
dialogue_ui.gd: start_dialogue(npc_name)
    ↓
Показ окна диалога, игрок вводит сообщение
    ↓
dialogue_ui.gd: send_message()
    ↓
api_client.gd: send_chat(npc_name, message)
    ↓
HTTP-запрос к FastAPI бэкенду
    ↓
api_client.gd: _on_chat_request_completed()
    ↓
Сигнал: chat_response_received
    ↓
dialogue_ui.gd: _on_chat_response_received()
    ↓
Показ ответа NPC
```

---

## Идеи расширения

### Добавить нового NPC
1. В `main.tscn` создайте экземпляр `npc.tscn`
2. Задайте имя и позицию
3. В `main.gd` в `get_npc_node()` добавьте сопоставление

### Добавить новый функционал
1. Добавьте параметры в `config.gd`
2. В `api_client.gd` добавьте новые методы API
3. Реализуйте логику в соответствующих скриптах

### Оптимизация
1. Уменьшите частоту обновления `NPC_STATUS_UPDATE_INTERVAL`
2. Используйте пул объектов для UI
3. Оптимизируйте слой коллизий TileMap

---

## Полезные ресурсы

- **Документация Godot:** https://docs.godotengine.org/
- **GDScript-учебник:** https://gdscript.com/
- **Документация FastAPI:** https://fastapi.tiangolo.com/

---

## Частые вопросы

**Q: Как изменить адрес API?**
A: Отредактируйте `API_BASE_URL` в `config.gd`.

**Q: Как добавить ещё NPC?**
A: Создайте экземпляр `npc.tscn`, задайте параметры и добавьте ссылку в `main.gd`.

**Q: Как настроить стиль окна диалога?**
A: Отредактируйте `dialogue_ui.tscn`, измените темы Panel и Label.

**Q: Как отключить отладочные логи?**
A: В `config.gd` установите `DEBUG_MODE = false`.
