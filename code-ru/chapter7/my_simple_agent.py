# my_simple_agent.py
from typing import Optional, Iterator
from hello_agents import SimpleAgent, HelloAgentsLLM, Config, Message
import re

class MySimpleAgent(SimpleAgent):
    """
    Переопределённый простой диалоговый Agent.
    Демонстрирует, как строить пользовательский Agent на основе базового класса фреймворка.
    """

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional['ToolRegistry'] = None,
        enable_tool_calling: bool = True
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(f"✅ {name} инициализирован, вызов инструментов: {'включён' if self.enable_tool_calling else 'отключён'}")

    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        """
        Переопределённый метод запуска — реализует простую диалоговую логику с поддержкой вызова инструментов.
        """
        print(f"🤖 {self.name} обрабатывает: {input_text}")

        # Формируем список сообщений
        messages = []

        # Добавляем системное сообщение (может содержать информацию об инструментах)
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        messages.append({"role": "system", "content": enhanced_system_prompt})

        # Добавляем историю сообщений
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        # Добавляем текущее пользовательское сообщение
        messages.append({"role": "user", "content": input_text})

        # Если вызов инструментов не включён — используем простую диалоговую логику
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            print(f"✅ {self.name} ответ завершён")
            return response

        # Логика с поддержкой многоитерационного вызова инструментов
        return self._run_with_tools(messages, input_text, max_tool_iterations, **kwargs)

    def _get_enhanced_system_prompt(self) -> str:
        """Сформировать расширенный системный промпт с информацией об инструментах"""
        base_prompt = self.system_prompt or "Ты полезный AI-ассистент."

        if not self.enable_tool_calling or not self.tool_registry:
            return base_prompt

        # Получаем описание инструментов
        tools_description = self.tool_registry.get_tools_description()
        if not tools_description or tools_description == "Инструменты недоступны":
            return base_prompt

        tools_section = "\n\n## Доступные инструменты\n"
        tools_section += "Ты можешь использовать следующие инструменты для ответа на вопросы:\n"
        tools_section += tools_description + "\n"

        tools_section += "\n## Формат вызова инструмента\n"
        tools_section += "Когда нужно использовать инструмент, применяй следующий формат:\n"
        tools_section += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"
        tools_section += "Например: `[TOOL_CALL:search:программирование на Python]` или `[TOOL_CALL:memory:recall=информация о пользователе]`\n\n"
        tools_section += "Результат вызова инструмента будет автоматически добавлен в диалог, и ты сможешь продолжить ответ на его основе.\n"

        return base_prompt + tools_section

    def _run_with_tools(self, messages: list, input_text: str, max_tool_iterations: int, **kwargs) -> str:
        """Логика выполнения с поддержкой вызова инструментов"""
        current_iteration = 0
        final_response = ""

        while current_iteration < max_tool_iterations:
            # Вызываем LLM
            response = self.llm.invoke(messages, **kwargs)

            # Проверяем наличие вызовов инструментов
            tool_calls = self._parse_tool_calls(response)

            if tool_calls:
                print(f"🔧 Обнаружено вызовов инструментов: {len(tool_calls)}")
                # Выполняем все вызовы инструментов и собираем результаты
                tool_results = []
                clean_response = response

                for call in tool_calls:
                    result = self._execute_tool_call(call['tool_name'], call['parameters'])
                    tool_results.append(result)
                    # Убираем маркер вызова инструмента из ответа
                    clean_response = clean_response.replace(call['original'], "")

                # Формируем сообщение с результатами инструментов
                messages.append({"role": "assistant", "content": clean_response})

                # Добавляем результаты инструментов
                tool_results_text = "\n\n".join(tool_results)
                messages.append({"role": "user", "content": f"Результаты выполнения инструментов:\n{tool_results_text}\n\nПожалуйста, дай полный ответ на основе этих результатов."})

                current_iteration += 1
                continue

            # Вызовов инструментов нет — это финальный ответ
            final_response = response
            break

        # Если превышено максимальное количество итераций, получаем последний ответ
        if current_iteration >= max_tool_iterations and not final_response:
            final_response = self.llm.invoke(messages, **kwargs)

        # Сохраняем в историю
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_response, "assistant"))
        print(f"✅ {self.name} ответ завершён")

        return final_response

    def _parse_tool_calls(self, text: str) -> list:
        """Разобрать вызовы инструментов из текста"""
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)

        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                'tool_name': tool_name.strip(),
                'parameters': parameters.strip(),
                'original': f'[TOOL_CALL:{tool_name}:{parameters}]'
            })

        return tool_calls

    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """Выполнить вызов инструмента"""
        if not self.tool_registry:
            return f"❌ Ошибка: реестр инструментов не настроен"

        try:
            # Интеллектуальный разбор параметров
            if tool_name == 'calculator':
                # Инструмент-калькулятор принимает выражение напрямую
                result = self.tool_registry.execute_tool(tool_name, parameters)
            else:
                # Остальные инструменты используют интеллектуальный разбор параметров
                param_dict = self._parse_tool_parameters(tool_name, parameters)
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    return f"❌ Ошибка: инструмент '{tool_name}' не найден"
                result = tool.run(param_dict)

            return f"🔧 Результат инструмента {tool_name}:\n{result}"

        except Exception as e:
            return f"❌ Вызов инструмента завершился ошибкой: {str(e)}"

    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """Интеллектуальный разбор параметров инструмента"""
        param_dict = {}

        if '=' in parameters:
            # Формат: key=value или action=search,query=Python
            if ',' in parameters:
                # Несколько параметров: action=search,query=Python,limit=3
                pairs = parameters.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        param_dict[key.strip()] = value.strip()
            else:
                # Один параметр: key=value
                key, value = parameters.split('=', 1)
                param_dict[key.strip()] = value.strip()
        else:
            # Параметр передан напрямую — определяем тип по инструменту
            if tool_name == 'search':
                param_dict = {'query': parameters}
            elif tool_name == 'memory':
                param_dict = {'action': 'search', 'query': parameters}
            else:
                param_dict = {'input': parameters}

        return param_dict

    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        """
        Пользовательский метод потоковой передачи ответа.
        """
        print(f"🌊 {self.name} начинает потоковую обработку: {input_text}")

        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": input_text})

        # Потоковый вызов LLM
        full_response = ""
        print("📝 Ответ в реальном времени: ", end="")
        for chunk in self.llm.stream_invoke(messages, **kwargs):
            full_response += chunk
            print(chunk, end="", flush=True)
            yield chunk

        print()  # Перевод строки

        # Сохраняем полный диалог в историю
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(full_response, "assistant"))
        print(f"✅ {self.name} потоковый ответ завершён")

    def add_tool(self, tool) -> None:
        """Добавить инструмент в Agent (вспомогательный метод)"""
        if not self.tool_registry:
            from hello_agents import ToolRegistry
            self.tool_registry = ToolRegistry()
            self.enable_tool_calling = True

        self.tool_registry.register_tool(tool)
        print(f"🔧 Инструмент '{tool.name}' добавлен")

    def has_tools(self) -> bool:
        """Проверить наличие доступных инструментов"""
        return self.enable_tool_calling and self.tool_registry is not None

    def remove_tool(self, tool_name: str) -> bool:
        """Удалить инструмент (вспомогательный метод)"""
        if self.tool_registry:
            self.tool_registry.unregister(tool_name)
            return True
        return False

    def list_tools(self) -> list:
        """Перечислить все доступные инструменты"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []
