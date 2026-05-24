from hello_agents.protocols.a2a.implementation import A2AServer, A2A_AVAILABLE

def create_calculator_agent():
    """Создаём агента-калькулятора"""
    if not A2A_AVAILABLE:
        print("A2A SDK не установлен, выполните: pip install a2a-sdk")
        return None

    print("Создаём агента-калькулятора")

    # Создаём A2A-сервер
    calculator = A2AServer(
        name="calculator-agent",
        description="Профессиональный агент для математических вычислений",
        version="1.0.0",
        capabilities={
            "math": ["addition", "subtraction", "multiplication", "division"],
            "advanced": ["power", "sqrt", "factorial"]
        }
    )

    # Добавляем навык базового вычисления
    @calculator.skill("add")
    def add_numbers(query: str) -> str:
        """Вычисление суммы"""
        try:
            # Простой разбор формата "вычисли 5 + 3"
            parts = query.replace("вычисли", "").replace("плюс", "+").replace("прибавить", "+")
            if "+" in parts:
                numbers = [float(x.strip()) for x in parts.split("+")]
                result = sum(numbers)
                return f"Результат: {' + '.join(map(str, numbers))} = {result}"
            else:
                return "Используйте формат: вычисли 5 + 3"
        except Exception as e:
            return f"Ошибка вычисления: {e}"

    @calculator.skill("multiply")
    def multiply_numbers(query: str) -> str:
        """Вычисление произведения"""
        try:
            parts = query.replace("вычисли", "").replace("умножить на", "*").replace("×", "*")
            if "*" in parts:
                numbers = [float(x.strip()) for x in parts.split("*")]
                result = 1
                for num in numbers:
                    result *= num
                return f"Результат: {' × '.join(map(str, numbers))} = {result}"
            else:
                return "Используйте формат: вычисли 5 * 3"
        except Exception as e:
            return f"Ошибка вычисления: {e}"

    @calculator.skill("info")
    def get_info(query: str) -> str:
        """Получить информацию об агенте"""
        return f"Я {calculator.name}, могу выполнять базовые математические вычисления. Поддерживаемые навыки: {list(calculator.skills.keys())}"

    print(f"Агент-калькулятор успешно создан, поддерживаемые навыки: {list(calculator.skills.keys())}")
    return calculator

# Создаём агента
calc_agent = create_calculator_agent()
if calc_agent:
    # Тестируем навыки
    print("\nТестируем навыки агента:")
    test_queries = [
        "получить информацию",
        "вычисли 10 + 5",
        "вычисли 6 * 7"
    ]

    for query in test_queries:
        if "информаци" in query:
            result = calc_agent.skills["info"](query)
        elif "+" in query:
            result = calc_agent.skills["add"](query)
        elif "*" in query or "×" in query:
            result = calc_agent.skills["multiply"](query)
        else:
            result = "Неизвестный тип запроса"

        print(f"  Запрос: {query}")
        print(f"  Ответ: {result}")
        print()
