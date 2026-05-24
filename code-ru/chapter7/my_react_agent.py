MY_REACT_PROMPT = """Ты AI-ассистент с возможностями рассуждения и действия. Ты можешь анализировать задачи, вызывать подходящие инструменты для получения информации и в итоге давать точные ответы.

## Доступные инструменты
{tools}

## Рабочий процесс
Строго следуй формату ниже, выполняя только один шаг за раз:

Thought: Твой процесс мышления — анализ задачи, декомпозиция и планирование следующего шага.
Action: Действие, которое ты решаешь предпринять; должно быть в одном из следующих форматов:
- `{{tool_name}}[{{tool_input}}]` — вызов указанного инструмента
- `Finish[итоговый ответ]` — когда у тебя достаточно информации для финального ответа

## Важные напоминания
1. Каждый ответ должен содержать обе части: Thought и Action
2. Формат вызова инструмента должен строго соблюдаться: имя_инструмента[аргумент]
3. Используй Finish только тогда, когда уверен, что располагаешь достаточной информацией
4. Если информации от инструмента недостаточно — продолжай использовать другие инструменты или тот же инструмент с другими параметрами

## Текущая задача
**Question:** {question}

## История выполнения
{history}

Теперь начинай рассуждение и действие:
"""

import re
from typing import Optional, List, Tuple
from hello_agents import ReActAgent, HelloAgentsLLM, Config, Message, ToolRegistry

class MyReActAgent(ReActAgent):
    """
    Переопределённый ReAct Agent — интеллектуальный агент, сочетающий рассуждение и действие.
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history: List[str] = []
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT
        print(f"✅ {name} инициализирован, максимальное количество шагов: {max_steps}")

    def run(self, input_text: str, **kwargs) -> str:
        """Запустить ReAct Agent"""
        self.current_history = []
        current_step = 0

        print(f"\n🤖 {self.name} начинает обработку вопроса: {input_text}")

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- Шаг {current_step} ---")

            # 1. Формируем промпт
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_str
            )

            # 2. Вызываем LLM
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm.invoke(messages, **kwargs)

            # 3. Разбираем вывод
            thought, action = self._parse_output(response_text)

            # 4. Проверяем условие завершения
            if action and action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer

            # 5. Выполняем вызов инструмента
            if action:
                tool_name, tool_input = self._parse_action(action)
                observation = self.tool_registry.execute_tool(tool_name, tool_input)
                self.current_history.append(f"Action: {action}")
                self.current_history.append(f"Observation: {observation}")

        # Достигнуто максимальное количество шагов
        final_answer = "Извините, я не смог выполнить эту задачу за отведённое количество шагов."
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer
