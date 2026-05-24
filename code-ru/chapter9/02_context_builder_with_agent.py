"""
Пример интеграции ContextBuilder с Agent

Демонстрирует, как интегрировать ContextBuilder в Agent, реализуя:
1. Агент с осознанием контекста
2. Автоматическое построение оптимизированного контекста
3. Совместную работу управления памятью и построения контекста
"""
from dotenv import load_dotenv
load_dotenv()
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.context import ContextBuilder, ContextConfig
from hello_agents.tools import MemoryTool, RAGTool
from hello_agents.core.message import Message
from datetime import datetime


class ContextAwareAgent(SimpleAgent):
    """Агент с осознанием контекста"""

    def __init__(self, name: str, llm: HelloAgentsLLM, **kwargs):
        super().__init__(name=name, llm=llm, **kwargs)


        # (Опционально)
        # self.memory_tool = MemoryTool(user_id=kwargs.get("user_id", "default"))
        # self.rag_tool = RAGTool(knowledge_base_path=kwargs.get("knowledge_base_path", "./kb"))

        # Инициализация построителя контекста
        self.context_builder = ContextBuilder(
            # memory_tool=self.memory_tool,
            # rag_tool=self.rag_tool,
            config=ContextConfig(max_tokens=4000)
        )

        self.conversation_history = []

    def run(self, user_input: str) -> str:
        """Запуск агента с автоматическим построением оптимизированного контекста"""

        # 1. Использование ContextBuilder для построения оптимизированного контекста
        optimized_context = self.context_builder.build(
            user_query=user_input,
            conversation_history=self.conversation_history,
            system_instructions=self.system_prompt
        )

        # 2. Вызов LLM с оптимизированным контекстом
        messages = [
            {"role": "system", "content": optimized_context},
            {"role": "user", "content": user_input}
        ]
        response = self.llm.invoke(messages)

        # 3. Обновление истории диалога
        self.conversation_history.append(
            Message(content=user_input, role="user", timestamp=datetime.now())
        )
        self.conversation_history.append(
            Message(content=response, role="assistant", timestamp=datetime.now())
        )

        # 4. Сохранение важных взаимодействий в систему памяти
        # self.memory_tool.run({
        #     "action": "add",
        #     "content": f"В: {user_input}\nО: {response[:200]}...",  # Краткое содержание
        #     "memory_type": "episodic",
        #     "importance": 0.6
        # })

        return response


def main():
    print("=" * 80)
    print("Пример интеграции ContextBuilder с Agent")
    print("=" * 80 + "\n")

    # Настройка LLM
    from hello_agents.core.llm import HelloAgentsLLM
    llm = HelloAgentsLLM()

    # Пример использования
    agent = ContextAwareAgent(
        name="Консультант по данным",
        llm=llm,
        system_prompt="Вы опытный консультант по инженерии данных на Python."
    )

    # Начало диалога
    response = agent.run("Как оптимизировать потребление памяти в Pandas?")
    print(f"Ответ ассистента:\n{response}\n")

    # Продолжение диалога
    response = agent.run("Можете привести конкретный пример кода?")
    print(f"Ответ ассистента:\n{response}\n")

    print("=" * 80)


if __name__ == "__main__":
    main()
