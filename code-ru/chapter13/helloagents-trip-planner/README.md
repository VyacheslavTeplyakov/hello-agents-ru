# HelloAgents Умный туристический помощник 🌍✈️

Умный помощник по планированию путешествий на основе фреймворка HelloAgents, интегрированный с сервисом карт AMap через протокол MCP. Обеспечивает персонализированную генерацию маршрутов.

## ✨ Возможности

- 🤖 **Планирование путешествий на основе ИИ**: SimpleAgent из фреймворка HelloAgents интеллектуально формирует подробные многодневные маршруты
- 🗺️ **Интеграция с картами AMap**: подключение к сервису карт через протокол MCP — поиск достопримечательностей, построение маршрутов, запрос погоды
- 🧠 **Умный вызов инструментов**: агент автоматически вызывает MCP-инструменты карт AMap для получения актуальных POI, маршрутов и погоды
- 🎨 **Современный фронтенд**: Vue3 + TypeScript + Vite, адаптивный дизайн, плавный пользовательский интерфейс
- 📱 **Полный набор функций**: рекомендации по проживанию, транспорту, питанию и времени посещения достопримечательностей

## 🏗️ Технологический стек

### Бэкенд
- **Фреймворк**: HelloAgents (на основе SimpleAgent)
- **API**: FastAPI
- **MCP-инструмент**: amap-mcp-server (карты AMap)
- **LLM**: поддержка различных провайдеров (OpenAI, DeepSeek и др.)

### Фронтенд
- **Фреймворк**: Vue 3 + TypeScript
- **Инструмент сборки**: Vite
- **UI-библиотека**: Ant Design Vue
- **Картографический сервис**: JavaScript API карт AMap
- **HTTP-клиент**: Axios

## 📁 Структура проекта

```
helloagents-trip-planner/
├── backend/                    # Серверная часть
│   ├── app/
│   │   ├── agents/            # Реализация агентов
│   │   │   └── trip_planner_agent.py
│   │   ├── api/               # Маршруты FastAPI
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py
│   │   │       └── map.py
│   │   ├── services/          # Сервисный слой
│   │   │   ├── amap_service.py
│   │   │   └── llm_service.py
│   │   ├── models/            # Модели данных
│   │   │   └── schemas.py
│   │   └── config.py          # Управление конфигурацией
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/                   # Клиентская часть
│   ├── src/
│   │   ├── components/        # Vue-компоненты
│   │   ├── services/          # API-сервисы
│   │   ├── types/             # TypeScript-типы
│   │   └── views/             # Страницы
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10+
- Node.js 16+
- API-ключи карт AMap (Web Service API и Web Client JS API)
- API-ключ LLM (OpenAI/DeepSeek и др.)

### Установка бэкенда

1. Перейти в директорию бэкенда
```bash
cd backend
```

2. Создать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Установить зависимости
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения
```bash
cp .env.example .env
# Отредактировать .env — ввести API-ключи
```

5. Запустить серверную часть
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Установка фронтенда

1. Перейти в директорию фронтенда
```bash
cd frontend
```

2. Установить зависимости
```bash
npm install
```

3. Настроить переменные окружения
```bash
# Создать файл .env, указать Web API Key и Web JS API Key карт AMap
cp .env.example .env
```

4. Запустить сервер разработки
```bash
npm run dev
```

5. Открыть в браузере `http://localhost:5173`

## 📝 Инструкция по использованию

1. На главной странице заполните данные о путешествии:
   - Город назначения
   - Даты и количество дней
   - Способ передвижения
   - Предпочтения по размещению
   - Теги интересов

2. Нажмите кнопку «Начать планирование путешествия»

3. Система выполнит следующие действия:
   - Вызовет агента HelloAgents для создания предварительного плана
   - Агент автоматически вызовет MCP-инструменты карт AMap для поиска достопримечательностей
   - Агент получит информацию о погоде и построит маршруты
   - Объединит все данные в полный план путешествия

4. Просмотр результатов:
   - Подробный дневной маршрут
   - Информация о достопримечательностях с метками на карте
   - Маршруты передвижения
   - Прогноз погоды
   - Рекомендации по питанию

## 🔧 Ключевая реализация

### Интеграция агента HelloAgents

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool

# Создаём MCP-инструмент карт AMap
amap_tool = MCPTool(
    name="amap",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": "your_api_key"},
    auto_expand=True
)

# Создаём агента планирования путешествий
agent = SimpleAgent(
    name="Помощник по планированию путешествий",
    llm=HelloAgentsLLM(),
    system_prompt="Ты профессиональный помощник по планированию путешествий..."
)

# Добавляем инструмент
agent.add_tool(amap_tool)
```

### Вызов MCP-инструментов

Агент может автоматически вызывать следующие MCP-инструменты карт AMap:
- `maps_text_search`: поиск POI (достопримечательностей)
- `maps_weather`: запрос погоды
- `maps_direction_walking_by_address`: построение пешеходного маршрута
- `maps_direction_driving_by_address`: построение маршрута на автомобиле
- `maps_direction_transit_integrated_by_address`: построение маршрута на общественном транспорте

## 📄 Документация API

После запуска серверной части документация доступна по адресу `http://localhost:8000/docs`.

Основные эндпоинты:
- `POST /api/trip/plan` — сформировать план путешествия
- `GET /api/map/poi` — поиск POI
- `GET /api/map/weather` — запрос погоды
- `POST /api/map/route` — построить маршрут

## 🤝 Руководство по вкладу

Приветствуются Pull Request и Issue!

## 📜 Лицензия

CC BY-NC-SA 4.0

## 🙏 Благодарности

- [HelloAgents](https://github.com/datawhalechina/Hello-Agents) — учебник по агентам
- [Фреймворк HelloAgents](https://github.com/jjyaoao/HelloAgents) — фреймворк для агентов
- [Открытая платформа карт AMap](https://lbs.amap.com/) — картографический сервис
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — MCP-сервер карт AMap

---

**HelloAgents Умный туристический помощник** — планирование путешествий стало простым и умным 🌈
