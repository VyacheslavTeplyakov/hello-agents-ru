# Weather MCP Server

MCP-сервер запроса реальной погоды на основе фреймворка HelloAgents.

## Возможности

- Запрос погоды в реальном времени
- Поддержка 12 крупных городов России и мира
- Использует API wttr.in (ключ не требуется)
- Основан на фреймворке HelloAgents

## Установка

```bash
pip install hello-agents requests
```

## Использование

### Прямой запуск

```bash
python server.py
```

### Использование в Claude Desktop

Отредактируйте `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) или `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### Использование в HelloAgents

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool

agent = SimpleAgent(name="Погодный ассистент", llm=HelloAgentsLLM())
weather_tool = MCPTool(server_command=["python", "server.py"])
agent.add_tool(weather_tool)

response = agent.run("Какая сегодня погода в Пекине?")
```

## Инструменты API

### get_weather

Получает текущую погоду в указанном городе.

**Параметры:**
- `city` (string): Название города (поддерживаются китайские и английские названия)

**Пример:**
```json
{
  "city": "北京"
}
```

**Ответ:**
```json
{
  "city": "北京",
  "temperature": 10.0,
  "feels_like": 9.0,
  "humidity": 94,
  "condition": "Light rain",
  "wind_speed": 1.7,
  "visibility": 10.0,
  "timestamp": "2025-10-09 13:25:03"
}
```

### list_supported_cities

Перечисляет все поддерживаемые города.

**Ответ:**
```json
{
  "cities": ["北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "武汉", "西安", "南京", "天津", "苏州"],
  "count": 12
}
```

### get_server_info

Получает информацию о сервере.

**Ответ:**
```json
{
  "name": "Weather MCP Server",
  "version": "1.0.0",
  "tools": ["get_weather", "list_supported_cities", "get_server_info"]
}
```

## Поддерживаемые города

Пекин, Шанхай, Гуанчжоу, Шэньчжэнь, Ханчжоу, Чэнду, Чунцин, Ухань, Сиань, Нанкин, Тяньцзинь, Сучжоу

Также поддерживается запрос любого города мира по его английскому названию.

## Лицензия

MIT License

## Авторы

HelloAgents Team
