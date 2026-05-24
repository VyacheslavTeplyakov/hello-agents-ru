"""
Интеллектуальный поисковый ассистент — система реального поиска на базе LangGraph + Tavily API
1. Понимание потребностей пользователя
2. Реальный поиск информации с использованием Tavily API
3. Генерация ответа на основе результатов поиска
"""

import asyncio
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Загружаем переменные окружения
load_dotenv()

# Определяем структуру состояния
class SearchState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str        # Запрос пользователя
    search_query: str      # Оптимизированный поисковый запрос
    search_results: str    # Результаты поиска Tavily
    final_answer: str      # Итоговый ответ
    step: str             # Текущий шаг

# Инициализируем модель и клиент Tavily
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL_ID", "gpt-4o-mini"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    temperature=0.7
)

# Инициализируем клиент Tavily
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def understand_query_node(state: SearchState) -> SearchState:
    """Шаг 1: Понимание запроса пользователя и формирование ключевых слов для поиска"""

    # Получаем последнее сообщение пользователя
    user_message = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    understand_prompt = f"""Проанализируй запрос пользователя: "{user_message}"

Выполни два задания:
1. Кратко изложи, что именно хочет узнать пользователь
2. Сформулируй наиболее подходящие ключевые слова для поиска (на любом языке, точно и конкретно)

Формат:
Понимание: [краткое изложение потребности]
Поисковые слова: [лучшие ключевые слова для поиска]"""

    response = llm.invoke([SystemMessage(content=understand_prompt)])

    # Извлекаем ключевые слова для поиска
    response_text = response.content
    search_query = user_message  # По умолчанию используем исходный запрос

    if "Поисковые слова:" in response_text:
        search_query = response_text.split("Поисковые слова:")[1].strip()
    elif "Ключевые слова для поиска:" in response_text:
        search_query = response_text.split("Ключевые слова для поиска:")[1].strip()

    return {
        "user_query": response.content,
        "search_query": search_query,
        "step": "understood",
        "messages": [AIMessage(content=f"Я понял вашу потребность: {response.content}")]
    }

def tavily_search_node(state: SearchState) -> SearchState:
    """Шаг 2: Реальный поиск с использованием Tavily API"""

    search_query = state["search_query"]

    try:
        print(f"🔍 Выполняю поиск: {search_query}")

        # Вызываем поисковый API Tavily
        response = tavily_client.search(
            query=search_query,
            search_depth="basic",
            include_answer=True,
            include_raw_content=False,
            max_results=5
        )

        # Обрабатываем результаты поиска
        search_results = ""

        # Предпочтительно используем сводный ответ Tavily
        if response.get("answer"):
            search_results = f"Сводный ответ:\n{response['answer']}\n\n"

        # Добавляем конкретные результаты поиска
        if response.get("results"):
            search_results += "Дополнительная информация:\n"
            for i, result in enumerate(response["results"][:3], 1):
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                search_results += f"{i}. {title}\n{content}\nИсточник: {url}\n\n"

        if not search_results:
            search_results = "К сожалению, ничего не найдено по данному запросу."

        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content=f"✅ Поиск завершён! Найдена релевантная информация, формирую ответ...")]
        }

    except Exception as e:
        error_msg = f"Ошибка при поиске: {str(e)}"
        print(f"❌ {error_msg}")

        return {
            "search_results": f"Поиск не удался: {error_msg}",
            "step": "search_failed",
            "messages": [AIMessage(content="❌ Возникла проблема с поиском, отвечу на основе имеющихся знаний")]
        }

def generate_answer_node(state: SearchState) -> SearchState:
    """Шаг 3: Генерация итогового ответа на основе результатов поиска"""

    # Проверяем, есть ли результаты поиска
    if state["step"] == "search_failed":
        # Если поиск не удался — отвечаем на основе знаний модели
        fallback_prompt = f"""Поисковый API временно недоступен. Пожалуйста, ответьте на вопрос пользователя, опираясь на свои знания:

Вопрос пользователя: {state['user_query']}

Дайте полезный ответ и укажите, что он основан на имеющихся знаниях."""

        response = llm.invoke([SystemMessage(content=fallback_prompt)])

        return {
            "final_answer": response.content,
            "step": "completed",
            "messages": [AIMessage(content=response.content)]
        }

    # Генерируем ответ на основе результатов поиска
    answer_prompt = f"""На основе следующих результатов поиска дайте пользователю полный и точный ответ:

Вопрос пользователя: {state['user_query']}

Результаты поиска:
{state['search_results']}

Требования:
1. Объедините результаты поиска и дайте точный, полезный ответ
2. Если вопрос технический, предоставьте конкретные решения или код
3. Укажите источники важной информации
4. Ответ должен быть структурированным и понятным
5. Если результаты поиска неполные, укажите это и предложите дополнительные рекомендации"""

    response = llm.invoke([SystemMessage(content=answer_prompt)])

    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)]
    }

# Строим рабочий процесс поиска
def create_search_assistant():
    workflow = StateGraph(SearchState)

    # Добавляем три узла
    workflow.add_node("understand", understand_query_node)
    workflow.add_node("search", tavily_search_node)
    workflow.add_node("answer", generate_answer_node)

    # Устанавливаем линейный процесс
    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "search")
    workflow.add_edge("search", "answer")
    workflow.add_edge("answer", END)

    # Компилируем граф
    memory = InMemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app

async def main():
    """Главная функция: запуск интеллектуального поискового ассистента"""

    # Проверяем наличие API-ключа
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ Ошибка: задайте TAVILY_API_KEY в файле .env")
        return

    app = create_search_assistant()

    print("🔍 Интеллектуальный поисковый ассистент запущен!")
    print("Использую Tavily API для поиска актуальной и достоверной информации")
    print("Поддерживаю любые вопросы: новости, технологии, знания и многое другое")
    print("(Введите 'quit' для выхода)\n")

    session_count = 0

    while True:
        user_input = input("🤔 Что вы хотите узнать: ").strip()

        if user_input.lower() in ['quit', 'q', 'выход', 'exit']:
            print("Спасибо за использование! До свидания! 👋")
            break

        if not user_input:
            continue

        session_count += 1
        config = {"configurable": {"thread_id": f"search-session-{session_count}"}}

        # Начальное состояние
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_query": "",
            "search_query": "",
            "search_results": "",
            "final_answer": "",
            "step": "start"
        }

        try:
            print("\n" + "="*60)

            # Выполняем рабочий процесс
            async for output in app.astream(initial_state, config=config):
                for node_name, node_output in output.items():
                    if "messages" in node_output and node_output["messages"]:
                        latest_message = node_output["messages"][-1]
                        if isinstance(latest_message, AIMessage):
                            if node_name == "understand":
                                print(f"🧠 Этап понимания: {latest_message.content}")
                            elif node_name == "search":
                                print(f"🔍 Этап поиска: {latest_message.content}")
                            elif node_name == "answer":
                                print(f"\n💡 Итоговый ответ:\n{latest_message.content}")

            print("\n" + "="*60 + "\n")

        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            print("Пожалуйста, повторите вопрос.\n")

if __name__ == "__main__":
    asyncio.run(main())
