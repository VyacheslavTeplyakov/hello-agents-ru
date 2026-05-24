#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 02: Архитектурный дизайн MemoryTool
Демонстрация многоуровневой архитектуры MemoryTool и MemoryManager
"""

from dotenv import load_dotenv
load_dotenv()
from typing import List, Optional, Dict, Any
from datetime import datetime
from hello_agents.tools import MemoryTool
from hello_agents.memory import MemoryConfig

class MemoryToolArchitectureDemo:
    """Класс демонстрации архитектуры MemoryTool"""

    def __init__(self):
        self.memory_config = MemoryConfig()
        self.memory_types = ["working", "episodic", "semantic", "perceptual"]

    def demonstrate_memory_tool_init(self):
        """Демонстрация процесса инициализации MemoryTool"""
        print("🏗️ Демонстрация архитектурного дизайна MemoryTool")
        print("=" * 50)

        print("📋 Процесс инициализации MemoryTool:")
        print("1. Создание объекта конфигурации MemoryConfig")
        print("2. Указание активируемых типов памяти")
        print("3. Инициализация менеджера MemoryManager")
        print("4. Включение различных модулей памяти согласно конфигурации")

        # Демонстрация инициализации MemoryTool
        memory_tool = MemoryTool(
            user_id="architecture_demo_user",
            memory_config=self.memory_config,
            memory_types=self.memory_types
        )

        print(f"\n✅ Инициализация MemoryTool завершена")
        print(f"👤 Идентификатор пользователя: {memory_tool.memory_manager.user_id}")
        print(f"🧠 Активные типы памяти: {memory_tool.memory_types}")
        print(f"⚙️ Объект конфигурации: {type(memory_tool.memory_config).__name__}")

        return memory_tool

    def demonstrate_memory_manager_architecture(self, memory_tool):
        """Демонстрация архитектуры на основе шаблона «Компоновщик» MemoryManager"""
        print("\n🔧 Архитектурный дизайн MemoryManager")
        print("-" * 40)

        print("MemoryManager использует шаблон «Компоновщик»:")
        print("- Унифицированный интерфейс операций с памятью")
        print("- Независимые компоненты типов памяти")
        print("- Гибкие возможности конфигурации и расширения")

        # Получение экземпляра MemoryManager
        memory_manager = memory_tool.memory_manager

        print(f"\n📊 Состояние MemoryManager:")
        print(f"Идентификатор пользователя: {memory_manager.user_id}")
        print(f"Тип конфигурации: {type(memory_manager.config).__name__}")
        print(f"Количество типов памяти: {len(memory_manager.memory_types)}")

        # Отображение состояния каждого типа памяти
        print(f"\n🧠 Компоненты типов памяти:")
        for memory_type, memory_instance in memory_manager.memory_types.items():
            print(f"  • {memory_type}: {type(memory_instance).__name__}")

    def demonstrate_memory_types_specialization(self, memory_tool):
        """Демонстрация специализированных особенностей четырёх типов памяти"""
        print("\n🎯 Специализированный дизайн четырёх типов памяти")
        print("-" * 40)

        memory_types_info = {
            "working": {
                "name": "Рабочая память",
                "features": ["ограниченная ёмкость", "быстрый доступ", "автоматическая очистка", "временное хранение"],
                "storage": "Хранение в оперативной памяти",
                "ttl": "Механизм TTL 60 минут"
            },
            "episodic": {
                "name": "Эпизодическая память",
                "features": ["последовательность событий", "временная последовательность", "богатый контекст", "связь с сессией"],
                "storage": "Гибридное хранение SQLite + Qdrant",
                "ttl": "Постоянное хранение"
            },
            "semantic": {
                "name": "Семантическая память",
                "features": ["концептуальные знания", "связи сущностей", "граф знаний", "семантическое рассуждение"],
                "storage": "Гибридное хранение Neo4j + Qdrant",
                "ttl": "Долгосрочное хранение"
            },
            "perceptual": {
                "name": "Перцептивная память",
                "features": ["мультимодальность", "кросс-модальный поиск", "перцептивные данные", "генерация контента"],
                "storage": "Векторное хранение по модальностям",
                "ttl": "Управление по важности"
            }
        }

        for memory_type, info in memory_types_info.items():
            print(f"\n📚 {info['name']} ({memory_type}):")
            print(f"   Особенности: {', '.join(info['features'])}")
            print(f"   Хранение: {info['storage']}")
            print(f"   Жизненный цикл: {info['ttl']}")

            # Добавление примеров памяти для демонстрации особенностей
            if memory_type == "working":
                memory_tool.run({
                    "action":"add",
                    "content":f"Демонстрация временного хранения {info['name']}",
                    "memory_type":memory_type,
                    "importance":0.6,
                    "demo_feature":"temporary_storage"
                })
            elif memory_type == "episodic":
                memory_tool.run({
                    "action":"add",
                    "content":f"Демонстрация записи событий {info['name']}",
                    "memory_type":memory_type,
                    "importance":0.7,
                    "event_type":"demonstration",
                    "session_context":"architecture_demo"
                })
            elif memory_type == "semantic":
                memory_tool.run({
                    "action":"add",
                    "content":f"{info['name']} используется для хранения концептуальных знаний и связей сущностей",
                    "memory_type":memory_type,
                    "importance":0.8,
                    "concept":"memory_architecture",
                    "domain":"cognitive_computing"
                })
            elif memory_type == "perceptual":
                memory_tool.run({
                    "action":"add",
                    "content":f"Демонстрация обработки мультимодальных данных {info['name']}",
                    "memory_type":memory_type,
                    "importance":0.6,
                    "modality":"text",
                    "data_type":"demonstration"
                })

    def demonstrate_unified_interface(self, memory_tool):
        """Демонстрация преимуществ унифицированного интерфейса"""
        print("\n🔗 Преимущества унифицированного интерфейса")
        print("-" * 40)

        print("Унифицированный метод execute обеспечивает:")
        print("• Согласованный способ вызова")
        print("• Гибкую передачу параметров")
        print("• Унифицированную обработку ошибок")
        print("• Упрощённый пользовательский опыт")

        # Демонстрация использования унифицированного интерфейса
        operations = [
            ("search", {"query": "демонстрация", "limit": 2}),
            ("summary", {"limit": 3}),
            ("stats", {}),
        ]

        print(f"\n🔧 Демонстрация операций через унифицированный интерфейс:")
        for operation, params in operations:
            print(f"\nОперация: {operation}")
            print(f"Параметры: {params}")
            result = memory_tool.run({"action":operation, **params})
            print(f"Результат: {result[:100]}..." if len(str(result)) > 100 else f"Результат: {result}")

    def demonstrate_extensibility(self):
        """Демонстрация расширяемости системы"""
        print("\n🚀 Дизайн расширяемости системы")
        print("-" * 40)

        print("Особенности расширяемости:")
        print("• Подключаемые типы памяти")
        print("• Настраиваемые бэкенды хранения")
        print("• Гибкие стратегии памяти")
        print("• Модульный дизайн компонентов")

        # Демонстрация пользовательской конфигурации
        custom_config = MemoryConfig()
        custom_config.working_memory_capacity = 100
        custom_config.working_memory_ttl_minutes = 120

        print(f"\n⚙️ Пример пользовательской конфигурации:")
        print(f"Ёмкость рабочей памяти: {custom_config.working_memory_capacity}")
        print(f"TTL рабочей памяти: {custom_config.working_memory_ttl_minutes} минут")

        # Демонстрация выборочного включения типов памяти
        selective_memory_tool = MemoryTool(
            user_id="selective_user",
            memory_config=custom_config,
            memory_types=["working", "semantic"]  # Включение только части типов
        )

        print(f"\n🎯 Пример выборочного включения:")
        print(f"Активные типы памяти: {selective_memory_tool.memory_types}")
        print("✅ Система поддерживает гибкую настройку под конкретные нужды")

def main():
    """Главная функция"""
    print("🏗️ Полная демонстрация архитектурного дизайна MemoryTool")
    print("Демонстрация многоуровневой архитектуры и паттернов проектирования системы памяти")
    print("=" * 60)

    try:
        demo = MemoryToolArchitectureDemo()

        # 1. Демонстрация инициализации MemoryTool
        memory_tool = demo.demonstrate_memory_tool_init()

        # 2. Демонстрация архитектуры MemoryManager
        demo.demonstrate_memory_manager_architecture(memory_tool)

        # 3. Демонстрация специализации типов памяти
        demo.demonstrate_memory_types_specialization(memory_tool)

        # 4. Демонстрация унифицированного интерфейса
        demo.demonstrate_unified_interface(memory_tool)

        # 5. Демонстрация расширяемости
        demo.demonstrate_extensibility()

        print("\n" + "=" * 60)
        print("🎉 Демонстрация архитектуры MemoryTool завершена!")
        print("=" * 60)

        print("\n✨ Ключевые особенности архитектурного дизайна:")
        print("1. 🏗️ Многоуровневая архитектура — разделение задач, чёткие обязанности")
        print("2. 🔧 Шаблон «Компоновщик» — гибкая комбинация, независимое управление")
        print("3. 🎯 Специализированный дизайн — чёткие особенности каждого типа памяти")
        print("4. 🔗 Унифицированный интерфейс — простота использования, согласованный опыт")
        print("5. 🚀 Высокая расширяемость — подключаемый дизайн, гибкая конфигурация")

        print("\n🎯 Принципы проектирования:")
        print("• Принцип единственной ответственности — каждый компонент сосредоточен на конкретной функции")
        print("• Принцип открытости/закрытости — открыт для расширения, закрыт для модификации")
        print("• Принцип инверсии зависимостей — зависимость от абстракций, не от конкретных реализаций")
        print("• Компоновка вместо наследования — гибкая комбинация, избегание сложного наследования")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
