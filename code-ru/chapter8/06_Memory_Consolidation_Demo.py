#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 06: Демонстрация механизма консолидации памяти
Показывает процесс интеллектуального преобразования кратковременной памяти в долговременную
"""

from dotenv import load_dotenv
load_dotenv()
import time
from datetime import datetime, timedelta
from hello_agents.tools import MemoryTool


class MemoryConsolidationDemo:
    """Демонстрационный класс консолидации памяти"""

    def __init__(self):
        self.memory_tool = MemoryTool(
            user_id="consolidation_demo_user",
            memory_types=["working", "episodic", "semantic", "perceptual"]
        )

    def setup_initial_memories(self):
        """Настройка исходных данных памяти"""
        print("📝 Настройка исходных данных памяти")
        print("=" * 50)

        # Добавляем рабочие воспоминания с разной важностью
        working_memories = [
            {
                "content": "Изучил базовые принципы архитектуры Transformer",
                "importance": 0.9,
                "topic": "deep_learning",
                "session": "study_session_1"
            },
            {
                "content": "Выполнил задачу по отладке кода на Python",
                "importance": 0.8,
                "topic": "programming",
                "task_type": "debugging"
            },
            {
                "content": "Участвовал в командном совещании по обсуждению прогресса проекта",
                "importance": 0.7,
                "topic": "teamwork",
                "meeting_type": "progress_review"
            },
            {
                "content": "Посмотрел прогноз погоды на сегодня",
                "importance": 0.3,
                "topic": "daily_life",
                "category": "routine"
            },
            {
                "content": "Прочитал статью о механизме внимания",
                "importance": 0.85,
                "topic": "research",
                "paper_type": "technical"
            },
            {
                "content": "Выпил чашку кофе",
                "importance": 0.2,
                "topic": "daily_life",
                "category": "routine"
            },
            {
                "content": "Решил сложную алгоритмическую задачу",
                "importance": 0.9,
                "topic": "problem_solving",
                "difficulty": "high"
            },
            {
                "content": "Разобрал файлы на рабочем столе",
                "importance": 0.4,
                "topic": "organization",
                "category": "maintenance"
            }
        ]

        print("Добавляем рабочие воспоминания:")
        for i, memory in enumerate(working_memories):
            content = memory.pop("content")
            importance = memory.pop("importance")

            result = self.memory_tool.run({"action":"add",
                                            "content":content,
                                            "memory_type":"working",
                                            "importance":importance,
                                            **memory})

            print(f"  {i+1}. {content[:40]}... (важность: {importance})")

        print(f"\n✅ Добавлено {len(working_memories)} рабочих воспоминаний")

        # Отображаем текущее состояние
        stats = self.memory_tool.run({"action":"stats"})
        print(f"\n📊 Текущая статистика памяти:\n{stats}")

    def demonstrate_consolidation_criteria(self):
        """Демонстрация критериев и процесса отбора для консолидации"""
        print("\n🎯 Демонстрация критериев консолидации памяти")
        print("-" * 50)

        print("Критерии консолидации:")
        print("• Фильтрация по порогу важности")
        print("• Сортировка по важности")
        print("• Обработка преобразования типов")
        print("• Обновление метаданных")

        # Получаем сводку текущей рабочей памяти
        print("\n📋 Состояние рабочей памяти перед консолидацией:")
        summary = self.memory_tool.run({"action":"summary", "limit":10})
        print(summary)

        # Тестируем влияние разных порогов консолидации
        thresholds = [0.5, 0.7, 0.8]

        for threshold in thresholds:
            print(f"\n🔍 Тест порога важности {threshold}:")

            # Имитируем процесс консолидации (без реального выполнения, только анализ)
            working_memories = []
            # Здесь должны браться реальные рабочие воспоминания; для упрощения демонстрации

            print(f"  Воспоминания, подходящие для консолидации при пороге {threshold}:")
            print(f"  • Воспоминания с важностью >= {threshold} будут консолидированы")
            print(f"  • Тип после консолидации: working → episodic")
            print(f"  • Повышение важности: importance × 1.1")

    def demonstrate_consolidation_process(self):
        """Демонстрация реального процесса консолидации"""
        print("\n🔄 Демонстрация процесса консолидации памяти")
        print("-" * 50)

        print("Этапы процесса консолидации:")
        print("1. Отбор подходящих воспоминаний")
        print("2. Сортировка по важности")
        print("3. Создание новых записей памяти")
        print("4. Обновление типа и метаданных")
        print("5. Добавление метки консолидации")

        # Выполняем консолидацию с разными порогами
        consolidation_tests = [
            (0.6, "Консолидация с низким порогом — консолидируется больше воспоминаний"),
            (0.8, "Консолидация с высоким порогом — консолидируются только самые важные")
        ]

        for threshold, description in consolidation_tests:
            print(f"\n🔄 {description} (порог: {threshold}):")

            # Получаем состояние до консолидации
            stats_before = self.memory_tool.run({"action":"stats"})
            print(f"Состояние до консолидации: {stats_before}")

            # Выполняем консолидацию
            start_time = time.time()
            consolidation_result = self.memory_tool.run({"action":"consolidate",
                                                          "from_type":"working",
                                                          "to_type":"episodic",
                                                          "importance_threshold":threshold})
            consolidation_time = time.time() - start_time

            print(f"Результат консолидации: {consolidation_result}")
            print(f"Время консолидации: {consolidation_time:.3f} сек")

            # Получаем состояние после консолидации
            stats_after = self.memory_tool.run({"action":"stats"})
            print(f"Состояние после консолидации: {stats_after}")

            # Просматриваем консолидированную эпизодическую память
            print(f"\n📚 Эпизодическая память после консолидации:")
            episodic_search = self.memory_tool.run({"action":"search",
                                                     "query":"",
                                                     "memory_type":"episodic",
                                                     "limit":5})
            print(episodic_search)

    def demonstrate_consolidation_metadata(self):
        """Демонстрация обработки метаданных при консолидации"""
        print("\n📋 Демонстрация обработки метаданных при консолидации")
        print("-" * 50)

        print("Обработка метаданных:")
        print("• Сохранение исходных метаданных")
        print("• Добавление метки консолидации")
        print("• Запись времени консолидации")
        print("• Сохранение ссылки на исходный ID")

        # Добавляем специальное рабочее воспоминание для демонстрации
        special_memory_result = self.memory_tool.run({"action":"add",
            "content":"Это специальное воспоминание для демонстрации обработки метаданных консолидации",
            "memory_type":"working",
            "importance":0.85,
            "special_tag":"metadata_demo",
            "original_context":"demonstration",
            "creation_purpose":"show_consolidation_metadata"
        })

        print(f"Добавлено специальное воспоминание: {special_memory_result}")

        # Выполняем консолидацию
        print(f"\n🔄 Выполняем консолидацию...")
        consolidation_result = self.memory_tool.run({"action":"consolidate",
                                                       "from_type":"working",
                                                       "to_type":"episodic",
                                                       "importance_threshold":0.8})

        print(f"Результат консолидации: {consolidation_result}")

        # Ищем консолидированное воспоминание и просматриваем метаданные
        print(f"\n🔍 Просмотр метаданных консолидированного воспоминания:")
        search_result = self.memory_tool.run({"action":"search",
                                                "query":"специальное воспоминание",
                                                "memory_type":"episodic",
                                                "limit":1})
        print(search_result)

    def demonstrate_multi_type_consolidation(self):
        """Демонстрация консолидации между несколькими типами памяти"""
        print("\n🔀 Демонстрация многотиповой консолидации памяти")
        print("-" * 50)

        print("Сценарии многотиповой консолидации:")
        print("• working → episodic (запись пережитого)")
        print("• working → semantic (извлечение знаний)")
        print("• episodic → semantic (обобщение опыта)")

        # Добавляем воспоминания для разных путей консолидации
        consolidation_candidates = [
            {
                "content": "Изучил принципы алгоритма обратного распространения в глубоком обучении",
                "memory_type": "working",
                "importance": 0.9,
                "learning_type": "concept",
                "suitable_for": "semantic"
            },
            {
                "content": "Сегодня днём участвовал в презентации по технологиям ИИ",
                "memory_type": "working",
                "importance": 0.8,
                "event_type": "meeting",
                "suitable_for": "episodic"
            },
            {
                "content": "В результате многократной практики освоил приёмы реализации Transformer",
                "memory_type": "episodic",
                "importance": 0.85,
                "experience_type": "skill",
                "suitable_for": "semantic"
            }
        ]

        print(f"\n📝 Добавляем кандидатов на консолидацию:")
        for memory in consolidation_candidates:
            content = memory.pop("content")
            memory_type = memory.pop("memory_type")
            importance = memory.pop("importance")
            suitable_for = memory.pop("suitable_for")

            result = self.memory_tool.run({"action":"add",
                                            "content":content,
                                            "memory_type":memory_type,
                                            "importance":importance,
                                            **memory})

            print(f"  • {content[:50]}... → подходит для консолидации в {suitable_for}")

        # Выполняем консолидацию по разным путям
        consolidation_paths = [
            ("working", "episodic", 0.75, "Консолидация записей пережитого"),
            ("working", "semantic", 0.85, "Консолидация извлечённых знаний"),
            ("episodic", "semantic", 0.8, "Консолидация обобщённого опыта")
        ]

        for from_type, to_type, threshold, description in consolidation_paths:
            print(f"\n🔄 {description} ({from_type} → {to_type}):")

            result = self.memory_tool.run({"action":"consolidate",
                                            "from_type":from_type,
                                            "to_type":to_type,
                                            "importance_threshold":threshold})

            print(f"Результат консолидации: {result}")

    def demonstrate_consolidation_benefits(self):
        """Демонстрация преимуществ консолидации памяти"""
        print("\n✨ Демонстрация преимуществ консолидации памяти")
        print("-" * 50)

        print("Преимущества консолидации:")
        print("• Долгосрочное сохранение важной информации")
        print("• Освобождение пространства рабочей памяти")
        print("• Формирование системы знаний")
        print("• Повышение эффективности поиска")

        # Получаем итоговое состояние системы памяти
        print(f"\n📊 Итоговое состояние системы памяти:")
        final_stats = self.memory_tool.run({"action":"stats"})
        print(final_stats)

        # Получаем сводку по каждому типу памяти
        print(f"\n📋 Сводка по каждому типу памяти:")

        memory_types = ["working", "episodic", "semantic"]
        for memory_type in memory_types:
            print(f"\nПамять типа {memory_type.upper()}:")
            type_summary = self.memory_tool.run({"action":"search",
                                                   "query":"",
                                                   "memory_type":memory_type,
                                                   "limit":3})
            print(type_summary)

        # Демонстрируем эффективность поиска после консолидации
        print(f"\n🔍 Тест эффективности поиска после консолидации:")
        search_queries = [
            ("глубокое обучение", "Тест поиска по разным типам памяти"),
            ("опыт обучения", "Тест поиска в консолидированной памяти"),
            ("важные концепции", "Тест поиска в семантической памяти")
        ]

        for query, description in search_queries:
            print(f"\nЗапрос: '{query}' ({description})")
            result = self.memory_tool.run({"action":"search",
                                            "query":query,
                                            "limit":3})
            print(result)

def main():
    """Главная функция"""
    print("🔄 Демонстрация механизма консолидации памяти")
    print("Показывает процесс интеллектуального преобразования кратковременной памяти в долговременную")
    print("=" * 60)

    try:
        demo = MemoryConsolidationDemo()

        # 1. Настройка исходных данных памяти
        demo.setup_initial_memories()

        # 2. Демонстрация критериев консолидации
        demo.demonstrate_consolidation_criteria()

        # 3. Демонстрация процесса консолидации
        demo.demonstrate_consolidation_process()

        # 4. Демонстрация обработки метаданных
        demo.demonstrate_consolidation_metadata()

        # 5. Демонстрация многотиповой консолидации
        demo.demonstrate_multi_type_consolidation()

        # 6. Демонстрация преимуществ консолидации
        demo.demonstrate_consolidation_benefits()

        print("\n" + "=" * 60)
        print("🎉 Демонстрация механизма консолидации памяти завершена!")
        print("=" * 60)

        print("\n✨ Ключевые возможности консолидации памяти:")
        print("1. 🎯 Интеллектуальный отбор — автоматический отбор по порогу важности")
        print("2. 🔄 Преобразование типов — гибкий механизм смены типа памяти")
        print("3. 📋 Сохранение метаданных — полное сохранение исходного контекста")
        print("4. ⚡ Автоматизированная обработка — автоматическая консолидация без вмешательства человека")
        print("5. 🔀 Многомаршрутная поддержка — поддержка нескольких путей консолидации")

        print("\n🎯 Принципы проектирования:")
        print("• Биомимикрия — моделирует процесс фиксации воспоминаний в мозге человека")
        print("• Интеллектуальность — автоматическое распознавание и обработка важной информации")
        print("• Гибкость — поддержка различных стратегий и путей консолидации")
        print("• Целостность — сохранение полноты и прослеживаемости воспоминаний")

        print("\n💡 Прикладная ценность:")
        print("• Управление знаниями — преобразование временного обучения в долгосрочные знания")
        print("• Накопление опыта — сохранение важного практического опыта")
        print("• Оптимизация системы — освобождение пространства кратковременной памяти")
        print("• Принятие решений — поддержка решений на основе исторического опыта")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
