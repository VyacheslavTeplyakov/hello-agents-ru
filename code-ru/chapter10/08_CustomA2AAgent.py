from hello_agents.protocols.a2a.implementation import A2AServer, A2A_AVAILABLE

def create_custom_agent():
    """Создаём пользовательского агента"""
    if not A2A_AVAILABLE:
        print("Сначала установите A2A SDK: pip install a2a-sdk")
        return None

    # Создаём агента
    agent = A2AServer(
        name="my-custom-agent",
        description="Мой пользовательский агент",
        capabilities={"custom": ["skill1", "skill2"]}
    )

    # Добавляем навыки
    @agent.skill("greet")
    def greet_user(name: str) -> str:
        """Приветствие пользователя"""
        return f"Привет, {name}! Я пользовательский агент."

    @agent.skill("calculate")
    def simple_calculate(expression: str) -> str:
        """Простое вычисление"""
        try:
            # Безопасное вычисление（только базовые операции）
            allowed_chars = set('0123456789+-*/(). ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"Результат: {expression} = {result}"
            else:
                return "Ошибка: поддерживаются только базовые математические операции"
        except Exception as e:
            return f"Ошибка вычисления: {e}"

    return agent

# Создаём и тестируем пользовательского агента
custom_agent = create_custom_agent()
if custom_agent:
    # Тестируем навыки
    print("Тест навыка приветствия:")
    result1 = custom_agent.skills["greet"]("Иван")
    print(result1)

    print("\nТест навыка вычисления:")
    result2 = custom_agent.skills["calculate"]("10 + 5 * 2")
    print(result2)
