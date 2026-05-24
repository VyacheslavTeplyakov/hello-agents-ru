"""
Примеры использования TerminalTool

Демонстрирует типичные сценарии использования TerminalTool:
1. Исследовательская навигация
2. Анализ файлов данных
3. Анализ файлов журналов
4. Анализ кодовой базы
"""

import os
from pathlib import Path
from hello_agents.tools import TerminalTool

# Получение директории, в которой находится скрипт
SCRIPT_DIR = Path(__file__).parent.absolute()


def demo_exploratory_navigation():
    """Демонстрация исследовательской навигации"""
    print("\n" + "=" * 80)
    print("Сценарий 1: Исследовательская навигация")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR))

    # Шаг 1: просмотр текущей директории
    print("1. Просмотр текущей директории:")
    result = terminal.run({"command": "ls -la"})
    print(result)

    # Шаг 2: просмотр Python-файлов
    print("\n2. Просмотр Python-файлов:")
    result = terminal.run({"command": "ls -la *.py"})
    print(result)

    # Шаг 3: поиск определённого файла
    print("\n3. Поиск файлов по шаблону:")
    result = terminal.run({"command": "find . -name '*codebase_maintainer.py'"})
    print(result)

    # Шаг 4: просмотр содержимого файла
    print("\n4. Просмотр содержимого файла:")
    result = terminal.run({"command": "head -n 20 codebase_maintainer.py"})
    print(result)


def demo_data_file_analysis():
    """Демонстрация анализа файлов данных"""
    print("\n" + "=" * 80)
    print("Сценарий 2: Анализ файлов данных")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "data"))

    # Просмотр первых строк CSV-файла
    print("1. Просмотр первых 5 строк CSV-файла:")
    result = terminal.run({"command": "head -n 5 sales_2024.csv"})
    print(result)

    # Подсчёт общего количества строк
    print("\n2. Подсчёт количества строк файла:")
    result = terminal.run({"command": "wc -l *.csv"})
    print(result)

    # Извлечение и подсчёт категорий продуктов
    print("\n3. Статистика распределения категорий продуктов:")
    result = terminal.run({"command": "tail -n +2 sales_2024.csv | cut -d',' -f3 | sort | uniq -c"})
    print(result)


def demo_log_analysis():
    """Демонстрация анализа файлов журналов"""
    print("\n" + "=" * 80)
    print("Сценарий 3: Анализ файлов журналов")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "logs"))

    # Просмотр последних записей об ошибках
    print("1. Просмотр последних записей об ошибках:")
    result = terminal.run({"command": "tail -n 50 app.log | grep ERROR"})
    print(result)

    # Статистика типов ошибок
    print("\n2. Статистика типов ошибок:")
    result = terminal.run({"command": "grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn"})
    print(result)

    # Поиск журналов за определённый период
    print("\n3. Поиск журналов за определённый период:")
    result = terminal.run({"command": "grep '2024-01-19 15:' app.log | tail -n 20"})
    print(result)


def demo_codebase_analysis():
    """Демонстрация анализа кодовой базы"""
    print("\n" + "=" * 80)
    print("Сценарий 4: Анализ кодовой базы")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "codebase"))

    # Подсчёт строк кода
    print("1. Подсчёт строк кода:")
    result = terminal.run({"command": "find . -name '*.py' -exec wc -l {} + | tail -n 1"})
    print(result)

    # Поиск всех комментариев TODO
    print("\n2. Поиск всех комментариев TODO:")
    result = terminal.run({"command": "grep -rn 'TODO' --include='*.py'"})
    print(result)

    # Поиск определений конкретных функций
    print("\n3. Поиск определений конкретных функций:")
    result = terminal.run({"command": "grep -rn 'def process_data' --include='*.py'"})
    print(result)


def demo_security_features():
    """Демонстрация функций безопасности"""
    print("\n" + "=" * 80)
    print("Демонстрация функций безопасности")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "project"))

    # Попытка выполнить запрещённую команду
    print("1. Попытка выполнить опасную команду (rm):")
    result = terminal.run({"command": "rm -rf /"})
    print(result)

    # Попытка обратиться к файлу вне рабочей директории
    print("\n2. Попытка обратиться к файлу вне рабочей директории:")
    result = terminal.run({"command": "cat /etc/passwd"})
    print(result)

    # Попытка выйти за пределы рабочей директории
    print("\n3. Попытка выйти за пределы рабочей директории через '..':")
    result = terminal.run({"command": "cd ../../../etc"})
    print(result)


def main():
    print("=" * 80)
    print("Примеры использования TerminalTool")
    print("=" * 80)

    # Демонстрация различных сценариев использования
    demo_exploratory_navigation()
    demo_data_file_analysis()
    demo_log_analysis()
    demo_codebase_analysis()
    demo_security_features()

    print("\n" + "=" * 80)
    print("Демонстрация завершена!")
    print("=" * 80)


if __name__ == "__main__":
    main()
