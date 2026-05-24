#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 08: Интеграция инструментов агента
Показывает, как интегрировать MemoryTool и RAGTool в фреймворк HelloAgents
"""

from dotenv import load_dotenv
load_dotenv()
import time
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool

class AgentIntegrationDemo:
    """Демонстрационный класс интеграции инструментов агента"""

    def __init__(self):
        self.setup_agent()

    def setup_agent(self):
        """Настройка агента и инструментов"""
        print("🤖 Настройка интеграции инструментов агента")
        print("=" * 50)

        # Инициализируем инструменты
        print("1. Инициализируем инструменты...")
        self.memory_tool = MemoryTool(
            user_id="agent_integration_user",
            memory_types=["working", "episodic", "semantic", "perceptual"]
        )

        self.rag_tool = RAGTool(
            knowledge_base_path="./agent_integration_kb",
            rag_namespace="agent_demo"
        )

        print("✅ MemoryTool и RAGTool инициализированы")

        # Создаём агента
        print("\n2. Создаём агента...")
        self.llm = HelloAgentsLLM()
        self.agent = SimpleAgent(
            name="Интеллектуальный учебный ассистент",
            llm=self.llm,
            system_prompt="Интеллектуальный ассистент с интегрированной памятью и функциями RAG"
        )

        print("✅ Агент создан")

        # Регистрируем инструменты
        print("\n3. Регистрируем инструменты...")
        self.tool_registry = ToolRegistry()
        self.tool_registry.register_tool(self.memory_tool)
        self.tool_registry.register_tool(self.rag_tool)
        self.agent.tool_registry = self.tool_registry

        print("✅ Инструменты зарегистрированы")

        # Отображаем состояние агента
        print(f"\n📊 Состояние агента:")
        print(f"  Имя: {self.agent.name}")
        print(f"  Описание: {self.agent.system_prompt}")
        print(f"  Доступные инструменты: {list(self.tool_registry._tools.keys())}")

    def demonstrate_tool_registry_pattern(self):
        """Демонстрация паттерна реестра инструментов"""
        print("\n🔧 Демонстрация паттерна реестра инструментов")
        print("-" * 50)

        print("Особенности паттерна реестра инструментов:")
        print("• 🔌 Унифицированный интерфейс инструментов")
        print("• 📋 Централизованное управление инструментами")
        print("• 🔄 Динамическая загрузка инструментов")
        print("• 🎯 Обнаружение возможностей инструментов")

        # Демонстрируем процесс регистрации инструментов
        print(f"\n🔧 Детали регистрации инструментов:")

        for tool_name, tool_instance in self.tool_registry._tools.items():
            print(f"\nИнструмент: {tool_name}")
            print(f"  Тип: {type(tool_instance).__name__}")
            print(f"  Описание: {tool_instance.description}")

            # Отображаем основные функции инструмента
            if tool_name == "memory":
                print(f"  Основные функции: управление памятью, поиск, консолидация, забывание")
                print(f"  Типы памяти: {tool_instance.memory_types}")
            elif tool_name == "rag":
                print(f"  Основные функции: обработка документов, интеллектуальные вопросы-ответы, поиск знаний")
                print(f"  Пространство имён: {tool_instance.rag_namespace}")

        # Демонстрируем механизм обнаружения инструментов
        print(f"\n🔍 Обнаружение возможностей инструментов:")
        available_tools = self.tool_registry.list_tools()
        print(f"Список доступных инструментов: {available_tools}")

        # Демонстрируем получение инструментов
        memory_tool = self.tool_registry.get_tool("memory")
        rag_tool = self.tool_registry.get_tool("rag")

        print(f"\n✅ Инструменты успешно получены:")
        print(f"  Инструмент Memory: {type(memory_tool).__name__}")
        print(f"  Инструмент RAG: {type(rag_tool).__name__}")

    def demonstrate_unified_interface(self):
        """Демонстрация паттерна унифицированного интерфейса"""
        print("\n🔗 Демонстрация паттерна унифицированного интерфейса")
        print("-" * 50)

        print("Преимущества унифицированного интерфейса:")
        print("• 🎯 Единообразный способ вызова")
        print("• 📝 Стандартизированная передача параметров")
        print("• 🛡️ Унифицированная обработка ошибок")
        print("• 🔄 Упрощённое переключение инструментов")

        # Демонстрируем единый интерфейс run
        print(f"\n🔗 Демонстрация единого интерфейса run:")

        # Операции с инструментом Memory
        print(f"\n1. Операции с инструментом Memory:")
        memory_operations = [
            ("add", {
                "content": "Изучил паттерны интеграции инструментов агента",
                "memory_type": "episodic",
                "importance": 0.8,
                "topic": "agent_integration"
            }),
            ("search", {
                "query": "интеграция агента",
                "limit": 2
            }),
            ("stats", {})
        ]

        for operation, params in memory_operations:
            print(f"  Операция: memory.run('{operation}', {params})")
            result = self.memory_tool.run({"action":operation, **params})
            print(f"  Результат: {str(result)[:100]}...")

        # Операции с инструментом RAG
        print(f"\n2. Операции с инструментом RAG:")

        # Сначала добавляем контент
        self.rag_tool.run({"action":"add_text",
                            "text":"Интеграция инструментов агента — ключевая особенность фреймворка HelloAgents, позволяющая агенту использовать несколько инструментов для выполнения сложных задач.",
                            "document_id":"agent_integration_guide"})

        rag_operations = [
            ("search", {
                "query": "интеграция инструментов агента",
                "limit": 2
            }),
            ("ask", {
                "question": "Что такое интеграция инструментов агента?",
                "limit": 2
            }),
            ("stats", {})
        ]

        for operation, params in rag_operations:
            print(f"  Операция: rag.run('{operation}', {params})")
            result = self.rag_tool.run({"action":operation, **params})
            print(f"  Результат: {str(result)[:100]}...")

    def demonstrate_collaborative_workflow(self):
        """Демонстрация совместного рабочего процесса"""
        print("\n🤝 Демонстрация совместного рабочего процесса")
        print("-" * 50)

        print("Сценарии совместной работы:")
        print("• 📚 Изучение нового знания → сохранение в RAG + запись в Memory")
        print("• 🔍 Обзор истории обучения → поиск в Memory + дополнение из RAG")
        print("• 💡 Применение знаний → запрос к RAG + обновление Memory")
        print("• 📊 Анализ обучения → сводная статистика по обоим инструментам")

        # Сценарий 1: Изучение нового знания
        print(f"\n📚 Сценарий 1: Изучение нового знания")

        # Добавляем учебные материалы в RAG
        learning_content = """# Паттерн проектирования: Наблюдатель

## Определение
Паттерн «Наблюдатель» определяет зависимость «один ко многим» между объектами: когда состояние одного объекта изменяется, все зависящие от него объекты получают уведомление и автоматически обновляются.

## Структура
- Subject (Субъект): хранит список наблюдателей, предоставляет методы регистрации и удаления
- Observer (Наблюдатель): определяет интерфейс обновления
- ConcreteSubject (Конкретный субъект): реализует интерфейс субъекта
- ConcreteObserver (Конкретный наблюдатель): реализует интерфейс наблюдателя

## Сценарии применения
- Обработка событий в GUI
- Архитектура модель-представление
- Системы публикации-подписки
"""

        rag_result = self.rag_tool.run({"action":"add_text",
                                         "text":learning_content,
                                         "document_id":"observer_pattern"})
        print(f"Результат добавления в RAG: {rag_result}")

        # Записываем учебную активность в систему памяти
        memory_result = self.memory_tool.run({"action":"add",
                                                "content":"Изучил паттерн проектирования «Наблюдатель»: определение, структуру и сценарии применения",
                                                "memory_type":"episodic",
                                                "importance":0.8,
                                                "topic":"design_patterns",
                                                "pattern_type":"observer"})
        print(f"Результат записи в Memory: {memory_result}")

        # Сценарий 2: Обзор истории обучения
        print(f"\n🔍 Сценарий 2: Обзор истории обучения")

        # Поиск истории обучения в системе памяти
        memory_search = self.memory_tool.run({"action":"search",
                                                "query":"изучение паттернов проектирования",
                                                "limit":3})
        print(f"Обзор истории обучения: {memory_search}")

        # Получение дополнительных знаний из RAG
        rag_search = self.rag_tool.run({"action":"search",
                                         "query":"паттерн Наблюдатель",
                                         "limit":2})
        print(f"Дополнение знаний: {rag_search}")

        # Сценарий 3: Применение знаний
        print(f"\n💡 Сценарий 3: Применение знаний")

        # Запрос к RAG о методах применения
        application_query = self.rag_tool.run({"action":"ask",
                                                "question":"В каких сценариях применяется паттерн «Наблюдатель»?",
                                                "limit":2})
        print(f"Запрос о сценариях применения: {application_query}")

        # Запись практики применения в память
        application_memory = self.memory_tool.run({"action":"add",
                                                     "content":"Изучил сценарии применения паттерна «Наблюдатель», планирую использовать в GUI-проекте",
                                                     "memory_type":"working",
                                                     "importance":0.7,
                                                     "application_context":"gui_project"})
        print(f"Запись применения: {application_memory}")

        # Сценарий 4: Анализ обучения
        print(f"\n📊 Сценарий 4: Анализ обучения")

        # Статистика системы памяти
        memory_stats = self.memory_tool.run({"action":"stats"})
        print(f"Статистика памяти: {memory_stats}")

        # Статистика системы RAG
        rag_stats = self.rag_tool.run({"action":"stats"})
        print(f"Статистика базы знаний: {rag_stats}")

        # Генерируем сводку обучения
        learning_summary = self.memory_tool.run({"action":"summary", "limit":5})
        print(f"Сводка обучения: {learning_summary}")

    def demonstrate_agent_orchestration(self):
        """Демонстрация возможностей оркестрации агента"""
        print("\n🎭 Демонстрация возможностей оркестрации агента")
        print("-" * 50)

        print("Особенности оркестрации агента:")
        print("• 🧠 Интеллектуальный выбор инструментов")
        print("• 🔄 Цепочечные вызовы инструментов")
        print("• 📊 Интеграция и анализ результатов")
        print("• 🎯 Целеориентированное выполнение")

        # Моделируем оркестрацию инструментов для сложной задачи
        print(f"\n🎭 Пример оркестрации сложной задачи:")
        print(f"Задача: Создать учебный план по машинному обучению")

        # Шаг 1: Получаем структуру знаний из RAG
        print(f"\nШаг 1: Получаем структуру знаний")

        # Добавляем знания о машинном обучении
        ml_content = """# Учебный путь по машинному обучению

## Начальный этап
1. Математическая база: линейная алгебра, теория вероятностей и статистика, математический анализ
2. Программирование: Python, NumPy, Pandas
3. Концепции машинного обучения: обучение с учителем, без учителя, с подкреплением

## Продвинутый этап
1. Реализация алгоритмов: реализация классических алгоритмов с нуля
2. Глубокое обучение: нейронные сети, CNN, RNN, Transformer
3. Практические проекты: сквозные проекты машинного обучения

## Экспертный этап
1. Оптимизация моделей: подбор гиперпараметров, сжатие моделей
2. Развёртывание и сопровождение: развёртывание, мониторинг, обновление моделей
3. Передовые технологии: новейшие публикации, проекты с открытым кодом
"""

        self.rag_tool.run({"action":"add_text",
                            "text":ml_content,
                            "document_id":"ml_learning_path"})

        knowledge_structure = self.rag_tool.run({"action":"ask",
                                                  "question":"Каков учебный путь по машинному обучению?",
                                                  "limit":3})
        print(f"Структура знаний: {knowledge_structure[:200]}...")

        # Шаг 2: Записываем учебный план в систему памяти
        print(f"\nШаг 2: Записываем учебный план")

        plan_memory = self.memory_tool.run({"action":"add",
                                             "content":"Составил учебный план по машинному обучению, включающий начальный, продвинутый и экспертный этапы",
                                             "memory_type":"episodic",
                                             "importance":0.9,
                                             "plan_type":"learning",
                                             "subject":"machine_learning"})
        print(f"Запись плана: {plan_memory}")

        # Шаг 3: Ищем соответствующий опыт обучения
        print(f"\nШаг 3: Поиск опыта обучения")

        experience_search = self.memory_tool.run({"action":"search",
                                                    "query":"учебный план опыт обучения",
                                                    "limit":3})
        print(f"Соответствующий опыт: {experience_search}")

        # Шаг 4: Генерируем итоговые рекомендации
        print(f"\nШаг 4: Генерируем итоговые рекомендации")

        final_advice = self.rag_tool.run({"action":"ask",
                                            "question":"Как составить эффективный учебный план по машинному обучению?",
                                            "limit":4})
        print(f"Итоговые рекомендации: {final_advice[:300]}...")

        # Записываем процесс оркестрации
        orchestration_memory = self.memory_tool.run({"action":"add",
                                                       "content":"Завершил составление учебного плана с применением совместной оркестрации RAG и Memory",
                                                       "memory_type":"working",
                                                       "importance":0.8,
                                                       "task_type":"orchestration"})
        print(f"\nЗапись оркестрации: {orchestration_memory}")

    def demonstrate_performance_analysis(self):
        """Демонстрация анализа производительности"""
        print("\n📊 Демонстрация анализа производительности")
        print("-" * 50)

        print("Показатели анализа производительности:")
        print("• ⏱️ Время отклика инструментов")
        print("• 🔄 Накладные расходы на переключение инструментов")
        print("• 💾 Использование памяти")
        print("• 🎯 Эффективность выполнения задач")

        # Тест производительности
        print(f"\n📊 Тест производительности:")

        # Тест производительности отдельных инструментов
        print(f"\n1. Производительность отдельных инструментов:")

        # Производительность инструмента Memory
        start_time = time.time()
        for i in range(5):
            self.memory_tool.run({"action":"add",
                                   "content":f"Воспоминание для теста производительности {i+1}",
                                   "memory_type":"working",
                                   "importance":0.5})
        memory_time = time.time() - start_time
        print(f"Инструмент Memory — 5 операций добавления: {memory_time:.3f} сек")

        # Производительность инструмента RAG
        start_time = time.time()
        for i in range(3):
            self.rag_tool.run({"action":"search",
                                "query":f"тестовый запрос {i+1}",
                                "limit":2})
        rag_time = time.time() - start_time
        print(f"Инструмент RAG — 3 операции поиска: {rag_time:.3f} сек")

        # Тест производительности совместной работы
        print(f"\n2. Производительность совместной работы:")

        start_time = time.time()

        # Моделируем совместный рабочий процесс
        self.rag_tool.run({"action":"add_text",
                            "text":"Это тестовый документ для оценки производительности",
                            "document_id":"perf_test"})

        self.memory_tool.run({"action":"add",
                                "content":"Выполнен тест производительности",
                                "memory_type":"working",
                                "importance":0.6})

        rag_result = self.rag_tool.run({"action":"search",
                                         "query":"тест производительности",
                                         "limit":1})

        memory_result = self.memory_tool.run({"action":"search",
                                                "query":"тест производительности",
                                                "limit":1})

        collaborative_time = time.time() - start_time
        print(f"Совместный рабочий процесс: {collaborative_time:.3f} сек")

        # Итоговый анализ производительности
        print(f"\n📈 Итоговый анализ производительности:")
        print(f"Среднее время ответа Memory: {memory_time/5:.3f} сек/операция")
        print(f"Среднее время ответа RAG: {rag_time/3:.3f} сек/операция")
        print(f"Эффективность совместной работы: {collaborative_time:.3f} сек/процесс")

        # Получаем итоговую статистику
        final_memory_stats = self.memory_tool.run({"action":"stats"})
        final_rag_stats = self.rag_tool.run({"action":"stats"})

        print(f"\n📊 Итоговое состояние системы:")
        print(f"Система Memory: {final_memory_stats}")
        print(f"Система RAG: {final_rag_stats}")

def main():
    """Главная функция"""
    print("🤖 Демонстрация интеграции инструментов агента")
    print("Показывает, как интегрировать MemoryTool и RAGTool в фреймворк HelloAgents")
    print("=" * 70)

    try:
        demo = AgentIntegrationDemo()

        # 1. Демонстрация паттерна реестра инструментов
        demo.demonstrate_tool_registry_pattern()

        # 2. Демонстрация паттерна унифицированного интерфейса
        demo.demonstrate_unified_interface()

        # 3. Демонстрация совместного рабочего процесса
        demo.demonstrate_collaborative_workflow()

        # 4. Демонстрация возможностей оркестрации агента
        demo.demonstrate_agent_orchestration()

        # 5. Демонстрация анализа производительности
        demo.demonstrate_performance_analysis()

        print("\n" + "=" * 70)
        print("🎉 Демонстрация интеграции инструментов агента завершена!")
        print("=" * 70)

        print("\n✨ Ключевые особенности интеграции агента:")
        print("1. 🔧 Паттерн реестра инструментов — унифицированное управление и обнаружение")
        print("2. 🔗 Единый интерфейс — единообразный способ вызова инструментов")
        print("3. 🤝 Совместный рабочий процесс — интеллектуальное взаимодействие инструментов")
        print("4. 🎭 Возможности оркестрации — автоматическая декомпозиция сложных задач")
        print("5. 📊 Мониторинг производительности — комплексная оценка производительности")

        print("\n🎯 Преимущества проектирования:")
        print("• Модульность — инструменты разрабатываются независимо, гибко комбинируются")
        print("• Расширяемость — поддержка динамического добавления новых инструментов")
        print("• Высокая связность — каждый инструмент сосредоточен на конкретной функции")
        print("• Низкая зависимость — минимизация зависимостей между инструментами")

        print("\n💡 Прикладная ценность:")
        print("• Интеллектуальный ассистент — создание многофункционального интеллектуального помощника")
        print("• Управление знаниями — корпоративная система управления знаниями")
        print("• Учебная платформа — система персонализированной учебной поддержки")
        print("• Поддержка принятия решений — принятие решений на основе знаний и опыта")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
