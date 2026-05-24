# Глава 9 — Примеры кода по контекстной инженерии

В этой директории собраны все примеры кода и демонстрационные файлы девятой главы «Контекстная инженерия».

## Структура директории

```
chapter9/
├── 01_context_builder_basic.py          # Базовое использование ContextBuilder
├── 02_context_builder_with_agent.py     # Интеграция ContextBuilder с Agent
├── 03_note_tool_operations.py           # Базовые операции NoteTool
├── 04_note_tool_integration.py          # Расширенная интеграция NoteTool
├── 05_terminal_tool_examples.py         # Примеры использования TerminalTool
├── 06_three_day_workflow.py             # Демонстрация полного трёхдневного рабочего процесса
├── codebase_maintainer.py               # Помощник по обслуживанию кодовой базы (основной компонент)
├── codebase/                            # Пример кодовой базы
│   ├── data_processor.py
│   ├── api_client.py
│   ├── utils.py
│   └── models.py
├── data/                                # Пример данных
│   └── sales_2024.csv
├── logs/                                # Пример логов
│   └── app.log
└── project/                             # Пример проекта
    ├── README.md
    └── main.py
```

## Быстрый старт

### 1. Настройка модели эмбеддингов

Для всех примеров, использующих функцию памяти, необходима настройка модели эмбеддингов. Самый простой способ:

```python
import os
# Использовать TF-IDF (не требует дополнительных зависимостей или загрузок)
os.environ['EMBED_MODEL_TYPE'] = 'tfidf'
os.environ['EMBED_MODEL_NAME'] = ''  # Обязательно очистить
```

### 2. Запуск примеров

```bash
# Перейти в директорию chapter9
cd code/chapter9

# Запустить пример TerminalTool (без LLM)
python 05_terminal_tool_examples.py

# Запустить базовые операции NoteTool (без LLM)
python 03_note_tool_operations.py

# Запустить полную демонстрацию рабочего процесса (требует настройки LLM)
python 06_three_day_workflow.py
```

## Описание примеров

### Базовые примеры

#### 01_context_builder_basic.py
- Базовое использование ContextBuilder
- Создание и управление пакетами контекста (ContextPacket)
- Ограничение токенов и приоритеты контекста

#### 02_context_builder_with_agent.py
- Интеграция ContextBuilder с SimpleAgent
- Автоматическое управление контекстом
- Обработка истории диалога

#### 03_note_tool_operations.py
- CRUD-операции NoteTool
- Поиск заметок и управление тегами
- Экспорт заметок

#### 04_note_tool_integration.py
- Интеграция NoteTool с ContextBuilder
- Долгосрочное отслеживание проектов
- Предложения на основе истории заметок

#### 05_terminal_tool_examples.py
- Типичные сценарии использования TerminalTool
- Навигационное исследование
- Анализ файлов данных
- Анализ логов
- Анализ кодовой базы
- Демонстрация функций безопасности

### Расширенные примеры

#### 06_three_day_workflow.py
**Полная демонстрация долгосрочного рабочего процесса агента**, включая:
- День первый: исследование кодовой базы
- День второй: анализ качества кода
- День третий: планирование задач рефакторинга
- Через неделю: проверка прогресса
- Демонстрация согласованности между сессиями
- Совместная работа трёх инструментов

Использует созданную нами пример кодовую базу (`./codebase`), содержащую:
- `data_processor.py` — модуль обработки данных (содержит несколько TODO)
- `api_client.py` — API-клиент (требует улучшения обработки ошибок)
- `utils.py` — вспомогательные функции (требуют оптимизации)
- `models.py` — модели данных (требуют дополнения валидации)

#### codebase_maintainer.py
**Основной компонент: помощник по обслуживанию кодовой базы**, интегрирующий:
- ContextBuilder — управление контекстом
- NoteTool — структурированные заметки
- TerminalTool — мгновенный доступ к файлам
- MemoryTool — память диалога (используется только рабочая память)

## Конфигурация

### Настройка модели эмбеддингов

Доступны три варианта:

#### Вариант 1: TF-IDF (рекомендуется для тестирования)

```python
import os
os.environ['EMBED_MODEL_TYPE'] = 'tfidf'
os.environ['EMBED_MODEL_NAME'] = ''  # Важно!
```

**Преимущества**:
- Не требует дополнительных зависимостей
- Не требует API-ключа
- Не требует загрузки модели

**Недостатки**:
- Ограниченные возможности семантического понимания

#### Вариант 2: Локальный Transformer (рекомендуется для офлайн-использования)

```python
import os
os.environ['EMBED_MODEL_TYPE'] = 'local'
os.environ['EMBED_MODEL_NAME'] = 'sentence-transformers/all-MiniLM-L6-v2'
os.environ['HF_TOKEN'] = 'your_huggingface_token'
```

**Требуется**:
1. Установить зависимости: `pip install sentence-transformers`
2. Токен Hugging Face (получить на https://huggingface.co/settings/tokens)
3. При первом запуске будет загружена модель (около 90 МБ)

**Способы настройки HF Token**:
```bash
# Способ 1: использовать huggingface-cli (рекомендуется, настройка один раз)
pip install huggingface-hub
huggingface-cli login

# Способ 2: задать в коде
os.environ['HF_TOKEN'] = 'hf_your_token_here'

# Способ 3: задать в командной строке
export HF_TOKEN="hf_your_token_here"
```

#### Вариант 3: DashScope Tongyi Qianwen (рекомендуется для продакшена)

```python
import os
os.environ['EMBED_MODEL_TYPE'] = 'dashscope'
os.environ['EMBED_MODEL_NAME'] = 'text-embedding-v3'
os.environ['EMBED_API_KEY'] = 'your_dashscope_api_key'
```

**Требуется**:
1. Регистрация: https://dashscope.aliyun.com/
2. Получить API-ключ
3. Установить зависимости: `pip install dashscope`

### Настройка LLM

Если используются примеры, требующие LLM, необходимо настроить:

```python
from hello_agents import HelloAgentsLLM

# Использовать настройки по умолчанию (требуется OPENAI_API_KEY)
llm = HelloAgentsLLM()

# Или указать явно
llm = HelloAgentsLLM(
    api_key="your_api_key",
    base_url="https://api.openai.com/v1",
    model="gpt-4"
)
```
Рекомендуется указывать настройки непосредственно в файле `.env`.


### Настройка памяти

`codebase_maintainer.py` настроен на использование только `working`-памяти, чтобы не требовалась векторная база данных Qdrant:

```python
self.memory_tool = MemoryTool(
    user_id=project_name,
    memory_types=["working"]  # Использовать только рабочую память
)
```

Если требуется более мощная память (episodic, semantic), необходимо установить и запустить Qdrant:

```bash
# Запустить Qdrant через Docker
docker run -p 6333:6333 qdrant/qdrant
```

## Описание файлов примеров

### Демонстрационные файлы данных

#### data/sales_2024.csv
Содержит 40+ записей о продажах со следующими полями:
- date (дата)
- product (продукт)
- category (категория: Electronics, Furniture)
- quantity (количество)
- price (цена)
- customer_id (ID клиента)
- region (регион: North, South, East, West)

#### logs/app.log
Имитация логов приложения за один день, включающих:
- Различные уровни логирования (INFO, WARNING, ERROR)
- Различные типы ошибок (DatabaseConnectionError, ValidationError и др.)
- Временные метки от 2024-01-19 14:00 до 23:30

#### codebase/
Содержит 4 модуля Python с 10+ комментариями TODO, подходящими для демонстрации:
- Анализа кода
- Поиска TODO
- Поиска определений функций
- Статистики кода

## Часто задаваемые вопросы

### Q1: RuntimeError: ни одна из моделей эмбеддингов недоступна

**Причина**: неправильная настройка модели эмбеддингов.

**Решение**: убедитесь, что `EMBED_MODEL_NAME` задан как пустая строка:

```python
os.environ['EMBED_MODEL_TYPE'] = 'tfidf'
os.environ['EMBED_MODEL_NAME'] = ''  # Эта строка обязательна!
```

### Q2: Ошибка подключения к Qdrant

**Причина**: конфигурация по умолчанию пытается подключиться к векторной базе данных Qdrant.

**Решение 1** (рекомендуется): использовать конфигурацию только с рабочей памятью (уже настроено в codebase_maintainer.py)

**Решение 2**: установить и запустить Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Q3: Ошибка загрузки модели Hugging Face

**Причина**: проблемы с сетью или отсутствие токена.

**Решения**:
1. Настроить HF Token (см. «Вариант 2» выше)
2. Или использовать зеркало: `export HF_ENDPOINT=https://hf-mirror.com`
3. Или переключиться на TF-IDF: `os.environ['EMBED_MODEL_TYPE'] = 'tfidf'`

### Q4: TerminalTool сообщает «команда не разрешена»

**Причина**: TerminalTool ограничен белым списком и допускает только безопасные команды.

**Решение**: использовать команды из разрешённого списка, например:
- Операции с файлами: ls, cat, head, tail, grep, find
- Обработка текста: awk, sed, cut, sort, uniq, wc
- Другие: pwd, cd, tree, stat

## Рекомендуемый порядок запуска

1. **Сначала запустить примеры без LLM**:
   - `03_note_tool_operations.py` — познакомиться с NoteTool
   - `05_terminal_tool_examples.py` — познакомиться с TerminalTool

2. **После настройки модели эмбеддингов**:
   - `01_context_builder_basic.py` — понять управление контекстом

3. **После настройки LLM**:
   - `02_context_builder_with_agent.py` — интеграция с Agent
   - `04_note_tool_integration.py` — расширенная интеграция
   - `06_three_day_workflow.py` — полный рабочий процесс

## Путь обучения

1. **Базовые концепции** → `01_context_builder_basic.py`
2. **Использование инструментов** → `03_note_tool_operations.py`, `05_terminal_tool_examples.py`
3. **Интеграция с Agent** → `02_context_builder_with_agent.py`
4. **Расширенное применение** → `04_note_tool_integration.py`
5. **Практический кейс** → `06_three_day_workflow.py`

## Советы

- Все примеры содержат конфигурацию модели эмбеддингов в начале файла
- Вариант с TF-IDF подходит для быстрого тестирования и демонстраций
- Для продакшена рекомендуется DashScope или локальный Transformer
- `codebase_maintainer.py` — полноценный практический кейс, заслуживающий углублённого изучения

## Дополнительная документация

- Подробная документация: `docs/chapter9/Глава 9 — Контекстная инженерия.md`
- Документация API: см. docstring каждого класса инструментов
- Главная страница проекта: README.md

## Вклад в проект

Если у вас есть вопросы или предложения, приветствуются Issue и PR!
