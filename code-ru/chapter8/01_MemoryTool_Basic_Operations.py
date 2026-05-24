#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 01: Базовые операции MemoryTool
Демонстрация основного метода execute и базовых операций MemoryTool
"""

from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from typing import List
from hello_agents.tools import MemoryTool

def memory_tool_execute_demo():
    """Демонстрация метода execute MemoryTool"""
    print("🧠 Демонстрация базовых операций MemoryTool")
    print("=" * 50)

    # Инициализация MemoryTool
    memory_tool = MemoryTool(
        user_id="demo_user",
        memory_types=["working", "episodic", "semantic", "perceptual"]
    )

    print("✅ Инициализация MemoryTool завершена")
    print(f"📋 Поддерживаемые операции: add, search, summary, stats, update, remove, forget, consolidate, clear_all")

    return memory_tool

def add_memory_demo(memory_tool):
    """Демонстрация добавления памяти — имитация процесса кодирования человеческой памяти"""
    print("\n📝 Демонстрация добавления памяти")
    print("-" * 30)

    # Добавление рабочей памяти
    result = memory_tool.run({
        "action":"add",
        "content":"Изучаю систему памяти фреймворка HelloAgents",
        "memory_type":"working",
        "importance":0.7,
        "task_type":"learning"
    })
    print(f"Рабочая память: {result}")

    # Добавление эпизодической памяти
    result = memory_tool.run({
        "action":"add",
        "content":"В 2024 году начал углублённо изучать технологии AI-агентов",
        "memory_type":"episodic",
        "importance":0.8,
        "event_type":"milestone",
        "location":"исследовательский центр"
    })
    print(f"Эпизодическая память: {result}")

    # Добавление семантической памяти
    result = memory_tool.run({
        "action":"add",
        "content":"Система памяти включает четыре типа: рабочую, эпизодическую, семантическую и перцептивную",
        "memory_type":"semantic",
        "importance":0.9,
        "concept":"memory_types",
        "domain":"cognitive_science"
    })
    print(f"Семантическая память: {result}")

    # Добавление перцептивной памяти
    result = memory_tool.run({
        "action":"add",
        "content":"Просмотрел архитектурную схему системы памяти и код реализации",
        "memory_type":"perceptual",
        "importance":0.6,
        "modality":"document",
        "source":"technical_documentation"
    })
    print(f"Перцептивная память: {result}")

def search_memory_demo(memory_tool):
    """Демонстрация поиска памяти — реализация поиска с семантическим пониманием"""
    print("\n🔍 Демонстрация поиска памяти")
    print("-" * 30)

    # Базовый поиск
    print("Базовый поиск — 'система памяти':")
    result = memory_tool.run({"action":"search", "query":"система памяти", "limit":3})
    print(result)

    # Поиск по типу
    print("\nПоиск по типу — 'память' в семантической памяти:")
    result = memory_tool.run({
        "action":"search",
        "query":"память",
        "memory_type":"semantic",
        "limit":2
    })
    print(result)

    # Установка порога важности
    print("\nПоиск высокоприоритетных воспоминаний:")
    result = memory_tool.run({
        "action":"search",
        "query":"AI Agent",
        "min_importance":0.7,
        "limit":3
    })
    print(result)

def memory_summary_demo(memory_tool):
    """Демонстрация сводки памяти — общий обзор системы"""
    print("\n📋 Демонстрация сводки памяти")
    print("-" * 30)

    # Получение сводки памяти
    result = memory_tool.run({"action":"summary", "limit":5})
    print("Сводка памяти:")
    print(result)

    # Получение статистики
    print("\n📊 Статистика:")
    result = memory_tool.run({"action": "stats"})
    print(result)

def memory_management_demo(memory_tool):
    """Демонстрация управления памятью — забывание и консолидация"""
    print("\n⚙️ Демонстрация управления памятью")
    print("-" * 30)

    # Добавление воспоминания с низкой важностью для теста забывания
    memory_tool.run({
        "action":"add",
        "content":"Это временное тестовое воспоминание с очень низкой важностью",
        "memory_type":"working",
        "importance":0.1
    })

    # Забывание на основе важности
    print("Забывание на основе важности (порог=0.2):")
    result = memory_tool.run({
        "action":"forget",
        "strategy":"importance_based",
        "threshold":0.2
    })
    print(result)

    # Консолидация памяти — перевод важных рабочих воспоминаний в эпизодические
    print("\nКонсолидация памяти (working → episodic):")
    result = memory_tool.run({
        "action":"consolidate",
        "from_type":"working",
        "to_type":"episodic",
        "importance_threshold":0.6
    })
    print(result)

def main():
    """Главная функция"""
    print("🚀 Полная демонстрация базовых операций MemoryTool")
    print("Демонстрация основных функций и методов системы памяти")
    print("=" * 60)

    try:
        # 1. Инициализация MemoryTool
        memory_tool = memory_tool_execute_demo()

        # 2. Демонстрация добавления памяти
        add_memory_demo(memory_tool)

        # 3. Демонстрация поиска памяти
        search_memory_demo(memory_tool)

        # 4. Демонстрация сводки памяти
        memory_summary_demo(memory_tool)

        # 5. Демонстрация управления памятью
        memory_management_demo(memory_tool)

        print("\n" + "=" * 60)
        print("🎉 Демонстрация базовых операций MemoryTool завершена!")
        print("=" * 60)

        print("\n✨ Продемонстрированные основные функции:")
        print("1. 🧠 Добавление и управление четырьмя типами памяти")
        print("2. 🔍 Интеллектуальный семантический поиск и фильтрация")
        print("3. 📋 Сводка памяти и статистический анализ")
        print("4. ⚙️ Консолидация памяти и избирательное забывание")

        print("\n🎯 Особенности дизайна:")
        print("• Унифицированный интерфейс execute, простые и согласованные операции")
        print("• Богатая поддержка метаданных для удобной классификации и поиска")
        print("• Интеллектуальная оценка важности и механизм временного затухания")
        print("• Стратегия управления памятью, имитирующая человеческое познание")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
