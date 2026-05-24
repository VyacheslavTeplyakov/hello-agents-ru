"""
Пример пользовательского MCP-сервера

Это простой MCP-сервер, предоставляющий базовые инструменты
для математических вычислений и обработки текста.
Служит для демонстрации того, как создать собственный MCP-сервер.

Способ запуска:
    python my_mcp_server.py

Или как MCP-сервер, вызываемый клиентом:
    MCPClient(["python", "my_mcp_server.py"])
"""

from fastmcp import FastMCP
import sys
import os

# Создаём экземпляр MCP-сервера
mcp = FastMCP("MyCustomServer")


# ==================== Математические инструменты ====================

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Калькулятор сложения

    Args:
        a: Первое число
        b: Второе число

    Returns:
        Сумма двух чисел
    """
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    Калькулятор вычитания

    Args:
        a: Уменьшаемое
        b: Вычитаемое

    Returns:
        Разность двух чисел
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Калькулятор умножения

    Args:
        a: Первое число
        b: Второе число

    Returns:
        Произведение двух чисел
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Калькулятор деления

    Args:
        a: Делимое
        b: Делитель

    Returns:
        Частное двух чисел

    Raises:
        ValueError: Когда делитель равен 0
    """
    if b == 0:
        raise ValueError("Делитель не может быть равен нулю")
    return a / b


# ==================== Инструменты обработки текста ====================

@mcp.tool()
def reverse_text(text: str) -> str:
    """
    Переворачивает текст

    Args:
        text: Текст для переворота

    Returns:
        Перевёрнутый текст
    """
    return text[::-1]


@mcp.tool()
def count_words(text: str) -> int:
    """
    Подсчитывает количество слов в тексте

    Args:
        text: Текст для подсчёта

    Returns:
        Количество слов
    """
    return len(text.split())


@mcp.tool()
def to_uppercase(text: str) -> str:
    """
    Преобразует текст в верхний регистр

    Args:
        text: Текст для преобразования

    Returns:
        Текст в верхнем регистре
    """
    return text.upper()


@mcp.tool()
def to_lowercase(text: str) -> str:
    """
    Преобразует текст в нижний регистр

    Args:
        text: Текст для преобразования

    Returns:
        Текст в нижнем регистре
    """
    return text.lower()


# ==================== Определение ресурсов ====================

@mcp.resource("config://server")
def get_server_config() -> str:
    """
    Получает конфигурацию сервера

    Returns:
        JSON-строка с конфигурацией сервера
    """
    import json
    config = {
        "name": "MyCustomServer",
        "version": "1.0.0",
        "tools_count": 8,
        "description": "Пример пользовательского MCP-сервера"
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


@mcp.resource("info://capabilities")
def get_capabilities() -> str:
    """
    Получает список возможностей сервера

    Returns:
        Текстовое описание списка возможностей
    """
    capabilities = """
Список возможностей сервера:

Математические вычисления:
- add: сложение
- subtract: вычитание
- multiply: умножение
- divide: деление

Обработка текста:
- reverse_text: переворот текста
- count_words: подсчёт слов
- to_uppercase: преобразование в верхний регистр
- to_lowercase: преобразование в нижний регистр

Ресурсы:
- config://server: конфигурация сервера
- info://capabilities: список возможностей (этот ресурс)
"""
    return capabilities.strip()


# ==================== Шаблоны промптов ====================

@mcp.prompt()
def math_helper() -> str:
    """
    Промпт помощника по математическим вычислениям

    Returns:
        Шаблон промпта
    """
    return """Ты помощник по математическим вычислениям. Ты можешь использовать следующие инструменты:
- add(a, b): вычислить сумму двух чисел
- subtract(a, b): вычислить разность двух чисел
- multiply(a, b): вычислить произведение двух чисел
- divide(a, b): вычислить частное двух чисел

Выбирай подходящий инструмент в зависимости от вопроса пользователя."""


@mcp.prompt()
def text_processor() -> str:
    """
    Промпт помощника по обработке текста

    Returns:
        Шаблон промпта
    """
    return """Ты помощник по обработке текста. Ты можешь использовать следующие инструменты:
- reverse_text(text): перевернуть текст
- count_words(text): подсчитать количество слов
- to_uppercase(text): преобразовать в верхний регистр
- to_lowercase(text): преобразовать в нижний регистр

Выбирай подходящий инструмент в зависимости от потребностей пользователя."""


# ==================== Основная программа ====================

if __name__ == "__main__":
    # Запускаем MCP-сервер
    # FastMCP автоматически обрабатывает транспорт через stdio
    mcp.run()
