#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 03: Подробное описание реализации WorkingMemory
Демонстрация стратегии гибридного поиска и механизма TTL рабочей памяти
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from hello_agents.tools import MemoryTool
from hello_agents.memory import MemoryItem
from dotenv import load_dotenv
load_dotenv()

class WorkingMemoryDemo:
    """Класс демонстрации рабочей памяти"""

    def __init__(self):
        self.memory_tool = MemoryTool(
            user_id="working_memory_demo",
            memory_types=["working"]  # Включение только рабочей памяти
        )

    def demonstrate_capacity_management(self):
        """Демонстрация управления ёмкостью и механизма TTL"""
        print("🧠 Демонстрация управления ёмкостью рабочей памяти")
        print("=" * 50)

        print("Особенности рабочей памяти:")
        print("• Ограниченная ёмкость (по умолчанию 50 записей)")
        print("• Механизм TTL (по умолчанию 60 минут)")
        print("• Автоматическая очистка устаревших воспоминаний")
        print("• Управление приоритетами (сортировка по важности)")

        # Добавление нескольких воспоминаний для демонстрации управления ёмкостью
        print(f"\n📝 Добавление тестовых воспоминаний...")
        for i in range(10):
            importance = 0.3 + (i * 0.07)  # Нарастающая важность
            self.memory_tool.run({
                "action":"add",
                "content":f"Тестовый элемент рабочей памяти {i+1} — важность {importance:.2f}",
                "memory_type":"working",
                "importance":importance,
                "test_id":i+1,
                "category":"capacity_test"
            })

        # Просмотр текущего состояния
        stats = self.memory_tool.run({"action":"stats"})
        print(f"Текущее состояние: {stats}")

        # Демонстрация сортировки по важности
        print(f"\n🔍 Поиск по важности:")
        result = self.memory_tool.run({
            "action":"search",
            "query":"тестовый элемент",
            "memory_type":"working",
            "limit":5
        })
        print(result)

    def demonstrate_mixed_retrieval_strategy(self):
        """Демонстрация стратегии гибридного поиска"""
        print("\n🔍 Демонстрация стратегии гибридного поиска")
        print("-" * 40)

        print("Стратегия гибридного поиска включает:")
        print("• Семантический поиск с векторизацией TF-IDF")
        print("• Поиск по ключевым словам")
        print("• Коэффициент временного затухания")
        print("• Корректировка весом важности")

        # Добавление различных типов воспоминаний для теста поиска
        test_memories = [
            {
                "content": "Python — высокоуровневый язык программирования с чистым и ясным синтаксисом",
                "importance": 0.8,
                "topic": "programming",
                "language": "python"
            },
            {
                "content": "Машинное обучение — важная ветвь искусственного интеллекта, включающая обучение с учителем и без учителя",
                "importance": 0.9,
                "topic": "ai",
                "domain": "machine_learning"
            },
            {
                "content": "Структуры данных включают базовые: массивы, связные списки, стеки, очереди",
                "importance": 0.7,
                "topic": "computer_science",
                "category": "data_structures"
            },
            {
                "content": "Анализ сложности алгоритмов использует нотацию O для описания временной и пространственной сложности",
                "importance": 0.8,
                "topic": "algorithms",
                "analysis": "complexity"
            }
        ]

        print(f"\n📝 Добавление тестовых воспоминаний...")
        for i, memory in enumerate(test_memories):
            content = memory.pop("content")
            importance = memory.pop("importance")
            self.memory_tool.run({
                "action":"add",
                "content":content,
                "memory_type":"working",
                "importance":importance,
                **memory
            })

        # Тестирование различных типов поиска
        search_tests = [
            ("программирование Python", "тест семантического соответствия"),
            ("обучение", "тест поиска по ключевым словам"),
            ("сложность", "тест частичного соответствия"),
            ("искусственный интеллект машинное обучение", "тест многословного соответствия")
        ]

        print(f"\n🔍 Тестирование гибридного поиска:")
        for query, description in search_tests:
            print(f"\nЗапрос: '{query}' ({description})")
            result = self.memory_tool.run({
                "action":"search",
                "query":query,
                "memory_type":"working",
                "limit":2
            })
            print(f"Результат: {result}")

    def demonstrate_time_decay_mechanism(self):
        """Демонстрация механизма временного затухания"""
        print("\n⏰ Демонстрация механизма временного затухания")
        print("-" * 40)

        print("Механизм временного затухания:")
        print("• Новые воспоминания имеют больший вес")
        print("• Вес старых воспоминаний снижается")
        print("• Имитация особенностей человеческой памяти")
        print("• Балансировка важности новой и старой информации")

        # Добавление воспоминаний разного «возраста» (имитация)
        time_test_memories = [
            ("Самая новая важная информация — только что изученная концепция", 0.7, "newest"),
            ("Относительно новая информация — содержание, изученное вчера", 0.7, "recent"),
            ("Относительно старая информация — содержание, изученное на прошлой неделе", 0.7, "older"),
            ("Самая старая информация — содержание давно прошедшего времени", 0.7, "oldest")
        ]

        print(f"\n📝 Добавление воспоминаний разных периодов...")
        for content, importance, age_category in time_test_memories:
            self.memory_tool.run({
                "action":"add",
                "content":content,
                "memory_type":"working",
                "importance":importance,
                "age_category":age_category,
                "timestamp_category":age_category
            })

        # Тест эффекта временного затухания
        print(f"\n🔍 Тест эффекта временного затухания:")
        result = self.memory_tool.run({
            "action":"search",
            "query":"изученное содержание",
            "memory_type":"working",
            "limit":4
        })
        print("Результаты поиска (обратите внимание на влияние времени на порядок):")
        print(result)

    def demonstrate_automatic_cleanup(self):
        """Демонстрация механизма автоматической очистки"""
        print("\n🧹 Демонстрация механизма автоматической очистки")
        print("-" * 40)

        print("Механизм автоматической очистки:")
        print("• Автоматическая очистка устаревших воспоминаний")
        print("• Очистка низкоприоритетных воспоминаний при превышении ёмкости")
        print("• Поддержание производительности и скорости отклика системы")
        print("• Имитация ограниченной ёмкости рабочей памяти")

        # Получение состояния перед очисткой
        stats_before = self.memory_tool.run({"action":"stats"})
        print(f"\nСостояние перед очисткой: {stats_before}")

        # Добавление воспоминаний с низкой важностью
        print(f"\n📝 Добавление воспоминаний с низкой важностью...")
        for i in range(5):
            self.memory_tool.run({
                "action":"add",
                "content":f"Временное воспоминание с низкой важностью {i+1}",
                "memory_type":"working",
                "importance":0.1 + i * 0.05,
                "temporary":True,
                "cleanup_test":True
            })

        # Запуск очистки на основе важности
        print(f"\n🧹 Выполнение очистки по важности...")
        cleanup_result = self.memory_tool.run({
            "action":"forget",
            "strategy":"importance_based",
            "threshold":0.3
        })
        print(f"Результат очистки: {cleanup_result}")

        # Получение состояния после очистки
        stats_after = self.memory_tool.run({"action":"stats"})
        print(f"\nСостояние после очистки: {stats_after}")

    def demonstrate_performance_characteristics(self):
        """Демонстрация производительностных характеристик"""
        print("\n⚡ Демонстрация производительностных характеристик")
        print("-" * 40)

        print("Производительностные особенности рабочей памяти:")
        print("• Хранение в оперативной памяти, сверхбыстрый доступ")
        print("• Нет дискового ввода-вывода, короткое время отклика")
        print("• Подходит для часто используемых временных данных")
        print("• Данные теряются при перезапуске системы (соответствует дизайну)")

        # Тест производительности
        print(f"\n⏱️ Тест производительности:")

        # Тест пакетного добавления
        start_time = time.time()
        for i in range(20):
            self.memory_tool.run({
                "action":"add",
                "content":f"Тестовое воспоминание производительности {i+1}",
                "memory_type":"working",
                "importance":0.5,
                "performance_test":True
            })
        add_time = time.time() - start_time
        print(f"Пакетное добавление 20 воспоминаний заняло: {add_time:.3f} сек")

        # Тест пакетного поиска
        start_time = time.time()
        for i in range(10):
            self.memory_tool.run({
                "action":"search",
                "query":f"тест производительности",
                "memory_type":"working",
                "limit":3
            })
        search_time = time.time() - start_time
        print(f"Пакетный поиск 10 раз занял: {search_time:.3f} сек")

        # Получение итоговой статистики
        final_stats = self.memory_tool.run("stats")
        print(f"\n📊 Итоговая статистика: {final_stats}")

def main():
    """Главная функция"""
    print("🧠 Подробное описание реализации WorkingMemory")
    print("Демонстрация основных характеристик и механизмов реализации рабочей памяти")
    print("=" * 60)

    try:
        demo = WorkingMemoryDemo()

        # 1. Демонстрация управления ёмкостью
        demo.demonstrate_capacity_management()

        # 2. Демонстрация стратегии гибридного поиска
        demo.demonstrate_mixed_retrieval_strategy()

        # 3. Демонстрация механизма временного затухания
        demo.demonstrate_time_decay_mechanism()

        # 4. Демонстрация механизма автоматической очистки
        demo.demonstrate_automatic_cleanup()

        # 5. Демонстрация производительностных характеристик
        demo.demonstrate_performance_characteristics()

        print("\n" + "=" * 60)
        print("🎉 Демонстрация реализации WorkingMemory завершена!")
        print("=" * 60)

        print("\n✨ Основные характеристики рабочей памяти:")
        print("1. 🧠 Ограниченная ёмкость — имитация ограничений рабочей памяти человека")
        print("2. ⚡ Высокоскоростной доступ — хранение в ОЗУ, быстрый отклик")
        print("3. 🔍 Гибридный поиск — семантика + ключевые слова + время + важность")
        print("4. ⏰ Временное затухание — приоритет новой информации, затухание старой")
        print("5. 🧹 Автоматическая очистка — механизм TTL + управление приоритетами")

        print("\n🎯 Концепция дизайна:")
        print("• Временность — хранение временной информации текущей сессии")
        print("• Эффективность — быстрый доступ и обработка")
        print("• Интеллектуальность — автоматическое управление и стратегии оптимизации")
        print("• Биомиметика — имитация характеристик рабочей памяти человека")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
