"""
Базовый пример использования ContextBuilder

Демонстрирует, как использовать ContextBuilder для построения
оптимизированного контекста, включая:
1. Инициализацию ContextBuilder
2. Подготовку истории диалога
3. Добавление воспоминаний
4. Построение структурированного контекста
"""
from dotenv import load_dotenv
load_dotenv()
from hello_agents.context import ContextBuilder, ContextConfig
from hello_agents.tools import MemoryTool, RAGTool
from hello_agents.core.message import Message
from datetime import datetime


def main():
    print("=" * 80)
    print("Базовый пример использования ContextBuilder")
    print("=" * 80 + "\n")

    # 1. Инициализация инструментов (опционально)
    print("1. Инициализация инструментов...")
    # memory_tool = MemoryTool(user_id="user123")
    # rag_tool = RAGTool(knowledge_base_path="./knowledge_base")

    # 2. Создание ContextBuilder
    print("2. Создание ContextBuilder...")
    config = ContextConfig(
        max_tokens=3000,
        reserve_ratio=0.2,
        min_relevance=0,  # Минимальный порог релевантности, 0 означает сохранение всей истории
        enable_compression=True
    )

    builder = ContextBuilder(
        # memory_tool=memory_tool,
        # rag_tool=rag_tool,
        config=config
    )

    # 3. Подготовка истории диалога
    print("3. Подготовка истории диалога...")
    conversation_history = [
        Message(content="Я разрабатываю инструмент для анализа данных", role="user", timestamp=datetime.now()),
        Message(content="Отлично! Инструменты для анализа данных обычно требуют обработки больших объёмов данных. Какой технологический стек вы планируете использовать?", role="assistant", timestamp=datetime.now()),
        Message(content="Я планирую использовать Python и Pandas, модуль чтения CSV уже готов", role="user", timestamp=datetime.now()),
        Message(content="Хороший выбор! Pandas очень мощен для обработки данных. Далее вам, вероятно, потребуется рассмотреть очистку и преобразование данных.", role="assistant", timestamp=datetime.now()),
    ]

    # 4. Добавление воспоминаний
    print("4. Добавление воспоминаний...")
    # memory_tool.run({
    #     "action": "add",
    #     "content": "Пользователь разрабатывает инструмент для анализа данных на Python и Pandas",
    #     "memory_type": "semantic",
    #     "importance": 0.8
    # })

    # memory_tool.run({
    #     "action": "add",
    #     "content": "Модуль чтения CSV уже разработан",
    #     "memory_type": "episodic",
    #     "importance": 0.7
    # })

    # 5. Построение контекста
    print("5. Построение контекста...\n")
    context_str = builder.build(
        user_query="Как оптимизировать потребление памяти в Pandas?",
        conversation_history=conversation_history,
        system_instructions="Вы опытный консультант по инженерии данных на Python. Ваши ответы должны: 1) давать конкретные и применимые рекомендации 2) объяснять технические принципы 3) приводить примеры кода"
    )

    print("=" * 80)
    print("Построенный контекст (структурированная строка):")
    print("=" * 80)
    print(context_str)
    print("=" * 80)
    print()

    # 6. Преобразование строки контекста в формат сообщений для LLM
    print("6. Передача контекста в LLM...")
    messages = [
        {"role": "system", "content": context_str},
        {"role": "user", "content": "Пожалуйста, ответьте"}

    ]

    from hello_agents.core.llm import HelloAgentsLLM
    llm = HelloAgentsLLM()
    # Примечание: для реального использования необходимо настроить LLM
    response = llm.invoke(messages)
    print(f"Ответ LLM: {response}")

    print("Демонстрация ContextBuilder завершена!")
    print("\nПодсказка: ContextBuilder возвращает структурированную строку контекста,")
    print("      которую можно передать непосредственно как system message в LLM.")


if __name__ == "__main__":
    main()
