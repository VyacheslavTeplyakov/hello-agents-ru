import re
from llm_client import HelloAgentsLLM
from tools import ToolExecutor, search

# Шаблон подсказки ReAct
REACT_PROMPT_TEMPLATE = """
Обратите внимание: вы — интеллектуальный ассистент, способный вызывать внешние инструменты.

Доступные инструменты:
{tools}

Пожалуйста, строго придерживайтесь следующего формата ответа:

Thought: Ваш мыслительный процесс — для анализа проблемы, декомпозиции задач, планирования следующего действия или осмысления результатов предыдущего шага.
Action: Действие, которое вы решаете предпринять; должно быть в одном из следующих форматов:
- `{{tool_name}}[{{tool_input}}]`: вызов доступного инструмента.
- `Finish[final answer]`: когда вы считаете, что получили финальный ответ.
- Когда вы собрали достаточно информации для ответа на итоговый вопрос пользователя, после поля Action: необходимо использовать `Finish[final answer]` для вывода финального ответа.


Теперь, пожалуйста, приступите к решению следующей задачи:
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []  # Сбрасываем историю перед каждым запуском
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- Шаг {current_step} ---")

            # 1. Форматируем подсказку
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)

            # 2. Вызываем LLM для «размышления»
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            if not response_text:
                print("Ошибка: LLM не вернул корректный ответ.")
                break

            # 3. Разбираем вывод LLM
            thought, action = self._parse_output(response_text)
            if thought: 
                print(f"🤔 Thought: {thought}")
            if not action: 
                print("Предупреждение: не удалось разобрать корректный Action; процесс остановлен.")
                break
            
            # 4. Исполняем Action
            if action.startswith("Finish"):
                # Если это инструкция Finish — извлекаем финальный ответ и завершаем
                final_answer = self._parse_action_input(action)
                print(f"🎉 Финальный ответ: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                self.history.append("Observation: Некорректный формат Action, пожалуйста, проверьте его.")
                continue

            print(f"🎬 Action: {tool_name}[{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            observation = tool_function(tool_input) if tool_function else f"Ошибка: инструмент с именем '{tool_name}' не найден."
            
            print(f"👀 Observation: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("Достигнут предел шагов; процесс остановлен.")
        return None

    def _parse_output(self, text: str):
        # Thought: совпадение до Action: или конца текста
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: совпадение до конца текста
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        return (match.group(1), match.group(2)) if match else (None, None)

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        return match.group(1) if match else ""

if __name__ == '__main__':
    llm = HelloAgentsLLM()
    tool_executor = ToolExecutor()
    search_desc = "Поисковая система в интернете. Используйте этот инструмент, когда нужно ответить на вопросы о текущих событиях, фактах и информации, отсутствующей в базе знаний."
    tool_executor.registerTool("Search", search_desc, search)
    agent = ReActAgent(llm_client=llm, tool_executor=tool_executor)
    question = "Какая последняя модель телефона Huawei? Каковы её ключевые преимущества?"
    agent.run(question)
