AGENT_SYSTEM_PROMPT = """
Ты умный туристический помощник. Твоя задача — анализировать запросы пользователя и решать задачи шаг за шагом с помощью доступных инструментов.

# Доступные инструменты:
- `get_weather(city: str)`: Запрос реальной погоды для указанного города.
- `get_attraction(city: str, weather: str)`: Поиск рекомендуемых достопримечательностей по городу и погоде.

# Требования к формату вывода:
Каждый твой ответ должен строго следовать этому формату — одна пара Thought и Action:

Thought: [Твой процесс мышления и план следующего шага]
Action: [Конкретное действие, которое ты хочешь выполнить]

Формат Action должен быть одним из следующих:
1. Вызов инструмента: function_name(arg_name="arg_value")
2. Завершение задачи: Finish[окончательный ответ]

# Важные замечания:
- Выводи только одну пару Thought-Action за раз
- Action должен быть на одной строке, без переносов строки
- Когда соберёшь достаточно информации для ответа, обязательно используй формат Action: Finish[окончательный ответ]

Начнём!
"""


import requests

def get_weather(city: str) -> str:
    """
    Запрашивает реальную информацию о погоде через API wttr.in.
    """
    # Точка API — запрашиваем данные в формате JSON
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # Выполняем сетевой запрос
        response = requests.get(url)
        # Проверяем код ответа (200 = успех)
        response.raise_for_status()
        # Разбираем возвращённые JSON-данные
        data = response.json()

        # Извлекаем текущие погодные условия
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        # Форматируем в естественный язык и возвращаем
        return f"Текущая погода в {city}: {weather_desc}, температура {temp_c} °C"

    except requests.exceptions.RequestException as e:
        # Обработка сетевых ошибок
        return f"Ошибка: проблема с сетью при запросе погоды — {e}"
    except (KeyError, IndexError) as e:
        # Обработка ошибок разбора данных
        return f"Ошибка: не удалось разобрать данные о погоде, возможно неверное название города — {e}"



import os
from tavily import TavilyClient

def get_attraction(city: str, weather: str) -> str:
    """
    Ищет и возвращает рекомендации достопримечательностей с помощью Tavily Search API
    на основе города и погоды.
    """
    # Получаем API-ключ из переменной окружения
    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return "Ошибка: переменная окружения TAVILY_API_KEY не настроена."

    # Инициализируем клиент Tavily
    tavily = TavilyClient(api_key=api_key)

    # Формируем точный поисковый запрос
    query = f"Самые стоящие достопримечательности '{city}' в погоду '{weather}' и причины посетить"

    try:
        # Вызываем API; include_answer=True возвращает сводный ответ
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        # Результаты Tavily уже достаточно чистые — используем напрямую
        # response['answer'] — сводный ответ на основе всех результатов поиска
        if response.get("answer"):
            return response["answer"]

        # Если сводного ответа нет — форматируем сырые результаты
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")

        if not formatted_results:
            return "К сожалению, рекомендации по достопримечательностям не найдены."

        return "По результатам поиска найдено следующее:\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"Ошибка: проблема при выполнении поиска через Tavily — {e}"


# Все инструменты в одном словаре для удобного вызова
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

from openai import OpenAI

class OpenAICompatibleClient:
    """
    Клиент для вызова любого LLM-сервиса, совместимого с интерфейсом OpenAI.
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        """Вызывает LLM API для генерации ответа."""
        print("Вызов языковой модели...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("Языковая модель успешно ответила.")
            return answer
        except Exception as e:
            print(f"Ошибка при вызове LLM API: {e}")
            return "Ошибка: проблема при обращении к языковой модели."

import re

# --- 1. Настройка LLM-клиента ---
# Замените на реальные учётные данные и адрес нужного вам сервиса
API_KEY = "YOUR_API_KEY"
BASE_URL = "YOUR_BASE_URL"
MODEL_ID = "YOUR_MODEL_ID"
os.environ['TAVILY_API_KEY'] = "YOUR_TAVILY_API_KEY"

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 2. Инициализация ---
user_prompt = "Привет, проверь сегодняшнюю погоду в Пекине и порекомендуй подходящую достопримечательность."
prompt_history = [f"Запрос пользователя: {user_prompt}"]

print(f"Ввод пользователя: {user_prompt}\n" + "="*40)

# --- 3. Основной цикл ---
for i in range(5):  # максимальное число итераций
    print(f"--- Итерация {i+1} ---\n")

    # 3.1. Формируем промпт
    full_prompt = "\n".join(prompt_history)

    # 3.2. Вызываем LLM для рассуждения
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    # Модель может выдать лишние пары Thought-Action — обрезаем
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("Лишние пары Thought-Action обрезаны")
    print(f"Вывод модели:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 3.3. Разбираем и выполняем действие
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "Ошибка: поле Action не найдено. Убедитесь, что ответ строго следует формату 'Thought: ... Action: ...'."
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"Задача выполнена. Финальный ответ: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"Ошибка: неизвестный инструмент '{tool_name}'"

    # 3.4. Записываем результат наблюдения
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
