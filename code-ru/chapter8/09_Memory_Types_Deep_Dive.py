#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример кода 09: Глубокий анализ четырёх типов памяти
Подробно рассматривает особенности реализации WorkingMemory, EpisodicMemory, SemanticMemory, PerceptualMemory
"""

from dotenv import load_dotenv
load_dotenv()
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from hello_agents.tools import MemoryTool

class MemoryTypesDeepDive:
    """Демонстрационный класс глубокого анализа четырёх типов памяти"""

    def __init__(self):
        self.setup_memory_systems()

    def setup_memory_systems(self):
        """Настройка различных систем памяти"""
        print("🧠 Глубокий анализ четырёх типов памяти")
        print("=" * 60)

        # Создаём специализированные экземпляры инструментов памяти
        self.working_memory_tool = MemoryTool(
            user_id="working_memory_user",
            memory_types=["working"]
        )

        self.episodic_memory_tool = MemoryTool(
            user_id="episodic_memory_user",
            memory_types=["episodic"]
        )

        self.semantic_memory_tool = MemoryTool(
            user_id="semantic_memory_user",
            memory_types=["semantic"]
        )

        self.perceptual_memory_tool = MemoryTool(
            user_id="perceptual_memory_user",
            memory_types=["perceptual"]
        )

        print("✅ Четыре системы памяти инициализированы")

    def demonstrate_working_memory(self):
        """Демонстрация особенностей рабочей памяти"""
        print("\n💭 Глубокий анализ рабочей памяти (Working Memory)")
        print("-" * 60)

        print("🔍 Особенности рабочей памяти:")
        print("• ⚡ Очень высокая скорость доступа (хранение только в RAM)")
        print("• 📏 Ограниченная ёмкость (по умолчанию 50 записей)")
        print("• ⏰ Автоматическое истечение срока (механизм TTL)")
        print("• 🔄 Подходит для хранения временной информации")

        # Демонстрируем ограничение ёмкости
        print(f"\n1. Демонстрация ограничения ёмкости:")
        print("Добавляем большое количество временных воспоминаний, наблюдаем за управлением ёмкостью...")

        for i in range(8):
            content = f"Временное рабочее воспоминание {i+1}: выполняется шаг задачи {i+1}"
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":content,
                                                    "memory_type":"working",
                                                    "importance":0.3 + (i * 0.1),
                                                    "task_step":i+1})
            print(f"  Добавлено воспоминание {i+1}: {result}")

        # Проверяем текущее состояние
        stats = self.working_memory_tool.run({"action":"stats"})
        print(f"\nТекущее состояние рабочей памяти: {stats}")

        # Демонстрируем механизм TTL
        print(f"\n2. Демонстрация механизма TTL (время жизни):")

        # Добавляем воспоминания с разными временными метками
        current_time = datetime.now()

        # Моделируем воспоминания разного «возраста»
        time_memories = [
            ("Только что возникшая мысль", 0, 0.8),
            ("Задача 5 минут назад", 5, 0.6),
            ("Напоминание 10 минут назад", 10, 0.4),
            ("Старая заметка давно", 30, 0.2)
        ]

        for content, minutes_ago, importance in time_memories:
            # Здесь мы моделируем разницу во времени
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":content,
                                                    "memory_type":"working",
                                                    "importance":importance,
                                                    "simulated_age_minutes":minutes_ago})
            print(f"  Добавлено воспоминание: {content} (смоделировано {minutes_ago} мин назад)")

        # Демонстрируем быстрый поиск
        print(f"\n3. Демонстрация быстрого поиска:")

        search_queries = ["задача", "мысль", "напоминание"]

        for query in search_queries:
            start_time = time.time()
            results = self.working_memory_tool.run({"action":"search",
                                                     "query":query,
                                                     "memory_type":"working",
                                                     "limit":3})
            search_time = time.time() - start_time
            print(f"  Запрос '{query}': {search_time:.4f} сек")
            print(f"    Результат: {results[:100]}...")

        # Демонстрируем автоматическую очистку
        print(f"\n4. Механизм автоматической очистки:")

        # Получаем статистику до очистки
        before_stats = self.working_memory_tool.run({"action":"stats"})
        print(f"До очистки: {before_stats}")

        # Запускаем очистку (путём забывания малозначимых воспоминаний)
        forget_result = self.working_memory_tool.run({"action":"forget",
                                                       "strategy":"importance_based",
                                                       "threshold":0.4})
        print(f"Результат очистки: {forget_result}")

        # Получаем статистику после очистки
        after_stats = self.working_memory_tool.run({"action":"stats"})
        print(f"После очистки: {after_stats}")

    def demonstrate_episodic_memory(self):
        """Демонстрация особенностей эпизодической памяти"""
        print("\n📖 Глубокий анализ эпизодической памяти (Episodic Memory)")
        print("-" * 60)

        print("🔍 Особенности эпизодической памяти:")
        print("• 📅 Полная запись временной последовательности")
        print("• 🎭 Богатая контекстная информация")
        print("• 🔗 Поддержка построения цепочек воспоминаний")
        print("• 💾 Постоянное хранение")

        # Демонстрируем полную запись событий
        print(f"\n1. Демонстрация полной записи событий:")

        # Моделируем полную сессию обучения
        learning_session = [
            {
                "content": "Начал изучать машинное обучение на Python",
                "context": "Начало обучения",
                "location": "Домашний кабинет",
                "mood": "сосредоточенный",
                "importance": 0.7
            },
            {
                "content": "Изучил математические принципы линейной регрессии",
                "context": "Теоретическое обучение",
                "chapter": "Глава 3",
                "difficulty": "средняя",
                "importance": 0.8
            },
            {
                "content": "Реализовал первую модель линейной регрессии",
                "context": "Практическое программирование",
                "code_lines": 45,
                "bugs_fixed": 2,
                "importance": 0.9
            },
            {
                "content": "Выполнил практические задания к занятию",
                "context": "Закрепление навыков",
                "exercises_completed": 5,
                "accuracy": 0.8,
                "importance": 0.6
            },
            {
                "content": "Подвёл итоги учебного занятия",
                "context": "Подведение итогов",
                "key_concepts": ["линейная регрессия", "градиентный спуск", "функция потерь"],
                "importance": 0.8
            }
        ]

        session_id = f"learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        for i, event in enumerate(learning_session):
            result = self.episodic_memory_tool.run({"action":"add",
                                                     "content":event["content"],
                                                     "memory_type":"episodic",
                                                     "importance":event["importance"],
                                                     "session_id":session_id,
                                                     "sequence_number":i+1,
                                                     **{k: v for k, v in event.items() if k not in ["content", "importance"]}})
            print(f"  Событие {i+1}: {result}")

        # Демонстрируем поиск по временной последовательности
        print(f"\n2. Демонстрация поиска по временной последовательности:")

        # Поиск в хронологическом порядке
        timeline_search = self.episodic_memory_tool.run({"action":"search",
                                                          "query":"обучение",
                                                          "memory_type":"episodic",
                                                          "limit":10})
        print(f"Временная шкала обучения: {timeline_search}")

        # Поиск по сессии
        session_search = self.episodic_memory_tool.run({"action":"search",
                                                         "query":"линейная регрессия",
                                                         "memory_type":"episodic",
                                                         "limit":5})
        print(f"Содержание сессии: {session_search}")

        # Демонстрируем богатство контекстной информации
        print(f"\n3. Демонстрация контекстной информации:")

        # Добавляем воспоминание с богатым контекстом
        rich_context_memory = {
            "content": "Посетил конференцию по технологиям ИИ",
            "event_type": "conference",
            "location": "Московский международный конгресс-центр",
            "speakers": ["Профессор Иванов", "Доктор Петров", "Инженер Сидоров"],
            "topics": ["Глубокое обучение", "Обработка естественного языка", "Компьютерное зрение"],
            "attendees_count": 200,
            "duration_hours": 6,
            "weather": "Солнечно",
            "transportation": "Метро",
            "networking_contacts": 3,
            "key_insights": ["Эволюция архитектуры Transformer", "Перспективы мультимодального обучения"],
            "follow_up_actions": ["Прочитать рекомендованные статьи", "Опробовать новый фреймворк"],
            "satisfaction_rating": 9
        }

        context_result = self.episodic_memory_tool.run({"action":"add",
                                                         "content":rich_context_memory["content"],
                                                         "memory_type":"episodic",
                                                         "importance":0.9,
                                                         **{k: v for k, v in rich_context_memory.items() if k != "content"}})
        print(f"Воспоминание с богатым контекстом: {context_result}")

        # Демонстрируем цепочки воспоминаний
        print(f"\n4. Построение цепочек воспоминаний:")

        # Создаём последовательность связанных воспоминаний
        memory_chain = [
            ("Увидел статью о GPT", "trigger", None),
            ("Решил углублённо изучить архитектуру Transformer", "decision", "trigger"),
            ("Скачал и прочитал статью 'Attention is All You Need'", "action", "decision"),
            ("Реализовал упрощённый механизм самовнимания", "implementation", "action"),
            ("Применил полученные знания в проекте", "application", "implementation")
        ]

        chain_memories = {}
        for content, chain_type, parent_type in memory_chain:
            parent_id = chain_memories.get(parent_type) if parent_type else None

            result = self.episodic_memory_tool.run({"action":"add",
                                                     "content":content,
                                                     "memory_type":"episodic",
                                                     "importance":0.7,
                                                     "chain_type":chain_type,
                                                     "parent_memory":parent_id,
                                                     "chain_id":"gpt_learning_chain"})

            # Извлекаем ID воспоминания (упрощённая обработка)
            memory_id = f"{chain_type}_memory"
            chain_memories[chain_type] = memory_id
            print(f"  Воспоминание цепочки: {content} (тип: {chain_type})")

        # Поиск по всей цепочке
        chain_search = self.episodic_memory_tool.run({"action":"search",
                                                        "query":"GPT Transformer",
                                                        "memory_type":"episodic",
                                                        "limit":8})
        print(f"Поиск по цепочке воспоминаний: {chain_search}")

    def demonstrate_semantic_memory(self):
        """Демонстрация особенностей семантической памяти"""
        print("\n🧠 Глубокий анализ семантической памяти (Semantic Memory)")
        print("-" * 60)

        print("🔍 Особенности семантической памяти:")
        print("• 🔗 Структурированное хранение в виде графа знаний")
        print("• 🎯 Абстрактное представление концепций и отношений")
        print("• 🔍 Поиск по семантическому сходству")
        print("• 🧮 Поддержка рассуждений и ассоциаций")

        # Демонстрируем хранение концепций
        print(f"\n1. Демонстрация хранения концептуальных знаний:")

        # Добавляем концептуальные знания разных типов
        concepts = [
            {
                "content": "Машинное обучение — раздел искусственного интеллекта, позволяющий компьютерам обучаться на данных с помощью алгоритмов",
                "concept_type": "definition",
                "domain": "artificial_intelligence",
                "keywords": ["машинное обучение", "искусственный интеллект", "алгоритмы", "данные", "паттерны"],
                "importance": 0.9
            },
            {
                "content": "Обучение с учителем использует размеченные данные для обучения модели; включает задачи классификации и регрессии",
                "concept_type": "category",
                "domain": "machine_learning",
                "parent_concept": "машинное обучение",
                "subcategories": ["классификация", "регрессия"],
                "importance": 0.8
            },
            {
                "content": "Градиентный спуск — алгоритм оптимизации, итеративно обновляющий параметры для минимизации функции потерь",
                "concept_type": "algorithm",
                "domain": "optimization",
                "mathematical_basis": "математический анализ",
                "applications": ["обучение нейронных сетей", "линейная регрессия"],
                "importance": 0.8
            },
            {
                "content": "Переобучение возникает, когда модель хорошо работает на обучающих данных, но плохо обобщается на новые данные",
                "concept_type": "problem",
                "domain": "machine_learning",
                "causes": ["высокая сложность модели", "недостаток обучающих данных"],
                "solutions": ["регуляризация", "кросс-валидация", "ранняя остановка"],
                "importance": 0.7
            }
        ]

        for concept in concepts:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":concept["content"],
                                                     "memory_type":"semantic",
                                                     "importance":concept["importance"],
                                                     **{k: v for k, v in concept.items() if k not in ["content", "importance"]}})
            print(f"  Сохранена концепция: {concept['concept_type']} - {result}")

        # Демонстрируем реляционные рассуждения
        print(f"\n2. Демонстрация реляционных рассуждений:")

        # Добавляем реляционные знания
        relationships = [
            {
                "content": "Глубокое обучение является подмножеством машинного обучения и использует многослойные нейронные сети",
                "relation_type": "is_subset_of",
                "subject": "глубокое обучение",
                "object": "машинное обучение",
                "strength": 0.9
            },
            {
                "content": "Свёрточные нейронные сети особенно хорошо подходят для обработки изображений",
                "relation_type": "suitable_for",
                "subject": "свёрточные нейронные сети",
                "object": "обработка изображений",
                "strength": 0.8
            },
            {
                "content": "Алгоритм обратного распространения используется для обучения нейронных сетей",
                "relation_type": "used_for",
                "subject": "обратное распространение",
                "object": "обучение нейронных сетей",
                "strength": 0.9
            }
        ]

        for relation in relationships:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":relation["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in relation.items() if k != "content"}})
            print(f"  Сохранено отношение: {relation['relation_type']} - {result}")

        # Демонстрируем семантический поиск
        print(f"\n3. Поиск по семантическому сходству:")

        semantic_queries = [
            "Что такое искусственный интеллект?",
            "Как предотвратить переобучение модели?",
            "Методы обучения нейронных сетей",
            "Технологии распознавания изображений"
        ]

        for query in semantic_queries:
            start_time = time.time()
            results = self.semantic_memory_tool.run({"action":"search",
                                                      "query":query,
                                                      "memory_type":"semantic",
                                                      "limit":3})
            search_time = time.time() - start_time
            print(f"  Запрос: '{query}' ({search_time:.4f} сек)")
            print(f"    Результат: {results[:150]}...")

        # Демонстрируем построение графа знаний
        print(f"\n4. Построение графа знаний:")

        # Добавляем сущности и отношения
        entities_and_relations = [
            {
                "content": "TensorFlow — фреймворк глубокого обучения, разработанный компанией Google",
                "entity_type": "framework",
                "developer": "Google",
                "domain": "deep_learning",
                "language": "Python",
                "year": 2015
            },
            {
                "content": "PyTorch — фреймворк глубокого обучения от Facebook, известный динамическими графами вычислений",
                "entity_type": "framework",
                "developer": "Facebook",
                "domain": "deep_learning",
                "feature": "dynamic_graph",
                "language": "Python"
            },
            {
                "content": "BERT — предобученная языковая модель на основе архитектуры Transformer",
                "entity_type": "model",
                "architecture": "Transformer",
                "task": "natural_language_processing",
                "training_method": "pre_training"
            }
        ]

        for item in entities_and_relations:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":item["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in item.items() if k != "content"}})
            print(f"  Сущность-отношение: {item['entity_type']} - {result}")

        # Получаем статистику семантической памяти
        semantic_stats = self.semantic_memory_tool.run({"action":"stats"})
        print(f"\nСтатистика семантической памяти: {semantic_stats}")

    def demonstrate_perceptual_memory(self):
        """Демонстрация особенностей перцептивной памяти"""
        print("\n👁️ Глубокий анализ перцептивной памяти (Perceptual Memory)")
        print("-" * 60)

        print("🔍 Особенности перцептивной памяти:")
        print("• 🎨 Поддержка мультимодальных данных")
        print("• 🔄 Кросс-модальный поиск по сходству")
        print("• 📊 Семантическое понимание перцептивных данных")
        print("• 🎯 Генерация и поиск контента")

        # Демонстрируем текстовую перцептивную память
        print(f"\n1. Текстовая перцептивная память:")

        text_perceptions = [
            {
                "content": "Прекрасное стихотворение: «Весенние воды сливаются с морем, луна над морем рождается вместе с приливом»",
                "modality": "text",
                "genre": "poetry",
                "emotion": "peaceful",
                "language": "russian",
                "aesthetic_value": 0.9
            },
            {
                "content": "Техническая документация: API-интерфейс возвращает данные в формате JSON, включающие код статуса и тело ответа",
                "modality": "text",
                "genre": "technical",
                "complexity": "medium",
                "language": "russian",
                "practical_value": 0.8
            }
        ]

        for perception in text_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.7,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  Текстовое восприятие: {perception['genre']} - {result}")

        # Демонстрируем визуальную перцептивную память (имитация)
        print(f"\n2. Визуальная перцептивная память (имитация):")

        # Имитируем графические данные
        image_perceptions = [
            {
                "content": "Красивый пейзажный снимок заката",
                "modality": "image",
                "file_path": "/simulated/sunset.jpg",
                "scene_type": "landscape",
                "colors": ["orange", "red", "purple"],
                "objects": ["sun", "clouds", "horizon"],
                "mood": "serene",
                "quality": "high"
            },
            {
                "content": "Схема технической архитектуры микросервисной системы",
                "modality": "image",
                "file_path": "/simulated/architecture.png",
                "diagram_type": "technical",
                "components": ["API Gateway", "Services", "Database"],
                "complexity": "high",
                "purpose": "documentation"
            }
        ]

        for perception in image_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.8,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  Визуальное восприятие: {perception['content']} - {result}")

        # Демонстрируем аудиальную перцептивную память (имитация)
        print(f"\n3. Аудиальная перцептивная память (имитация):")

        audio_perceptions = [
            {
                "content": "Прекрасное классическое музыкальное произведение",
                "modality": "audio",
                "file_path": "/simulated/classical.mp3",
                "genre": "classical",
                "instruments": ["piano", "violin", "cello"],
                "tempo": "andante",
                "emotion": "elegant",
                "duration_seconds": 240
            },
            {
                "content": "Запись технической конференции, обсуждение тенденций развития ИИ",
                "modality": "audio",
                "file_path": "/simulated/conference.wav",
                "content_type": "speech",
                "topic": "artificial_intelligence",
                "speakers": 3,
                "language": "russian",
                "duration_seconds": 1800
            }
        ]

        for perception in audio_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.7,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  Аудиальное восприятие: {perception['content']} - {result}")

        # Демонстрируем кросс-модальный поиск
        print(f"\n4. Демонстрация кросс-модального поиска:")

        cross_modal_queries = [
            ("красивый пейзаж", "Поиск контента, связанного с визуальной красотой"),
            ("техническая документация", "Поиск мультимодального технического контента"),
            ("музыка и искусство", "Поиск воспоминаний, связанных с искусством"),
            ("конференция и обсуждение", "Поиск контента, связанного с общением")
        ]

        for query, description in cross_modal_queries:
            results = self.perceptual_memory_tool.run({"action":"search",
                                                        "query":query,
                                                        "memory_type":"perceptual",
                                                        "limit":3})
            print(f"  Кросс-модальный запрос: '{query}' ({description})")
            print(f"    Результат: {results[:120]}...")

        # Демонстрируем анализ перцептивных признаков
        print(f"\n5. Анализ перцептивных признаков:")

        # Получаем статистику перцептивной памяти
        perceptual_stats = self.perceptual_memory_tool.run({"action":"stats"})
        print(f"Статистика перцептивной памяти: {perceptual_stats}")

        # Анализируем распределение по модальностям
        modality_analysis = self.perceptual_memory_tool.run({"action":"search",
                                                              "query":"анализ модальности",
                                                              "memory_type":"perceptual",
                                                              "limit":10})
        print(f"Анализ распределения по модальностям: {modality_analysis}")

    def demonstrate_memory_interactions(self):
        """Демонстрация взаимодействия четырёх типов памяти"""
        print("\n🔄 Демонстрация взаимодействия четырёх типов памяти")
        print("-" * 60)

        print("🔍 Паттерны взаимодействия памяти:")
        print("• 🔄 Рабочая → эпизодическая (фиксация важных событий)")
        print("• 📚 Эпизодическая → семантическая (абстрагирование опыта)")
        print("• 👁️ Перцептивная → другие (интеграция мультимодальной информации)")
        print("• 🧠 Семантическая → рабочая (активация знаний)")

        # Моделируем полный процесс обучения
        print(f"\nМоделирование полного процесса обучения:")

        # 1. Перцептивный этап: получение мультимодальной информации
        print(f"\n1. Перцептивный этап — получение информации:")

        perceptual_input = self.perceptual_memory_tool.run({"action":"add",
                                                             "content":"Просмотрел видеоурок по глубокому обучению",
                                                             "memory_type":"perceptual",
                                                             "importance":0.8,
                                                             "modality":"video",
                                                             "topic":"deep_learning",
                                                             "duration_minutes":45,
                                                             "quality":"high"})
        print(f"Перцептивная память: {perceptual_input}")

        # 2. Этап рабочей памяти: временная обработка и осмысление
        print(f"\n2. Этап рабочей памяти — временная обработка:")

        working_thoughts = [
            "Понял базовые принципы свёрточных нейронных сетей",
            "Нужно запомнить шаги вычисления обратного распространения",
            "Вспомнились ранее изученные знания по линейной алгебре",
            "Планирую реализовать простую модель CNN"
        ]

        for thought in working_thoughts:
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":thought,
                                                    "memory_type":"working",
                                                    "importance":0.6,
                                                    "processing_stage":"active_thinking"})
            print(f"  Рабочая память: {thought[:30]}... - {result}")

        # 3. Эпизодический этап: запись полного учебного события
        print(f"\n3. Эпизодический этап — запись события:")

        episodic_event = self.episodic_memory_tool.run({"action":"add",
                                                         "content":"Завершил изучение видеоурока по глубокому обучению, понял ключевые концепции CNN",
                                                         "memory_type":"episodic",
                                                         "importance":0.9,
                                                         "event_type":"learning_session",
                                                         "duration_minutes":45,
                                                         "location":"Дома",
                                                         "learning_outcome":"понимание принципов CNN",
                                                         "next_action":"практическое программирование"})
        print(f"Эпизодическая память: {episodic_event}")

        # 4. Семантический этап: абстрактное сохранение знаний
        print(f"\n4. Семантический этап — абстрагирование знаний:")

        semantic_knowledge = [
            {
                "content": "Свёрточные нейронные сети извлекают признаки изображений через свёрточные слои; подходят для задач компьютерного зрения",
                "concept": "CNN",
                "domain": "deep_learning",
                "application": "computer_vision"
            },
            {
                "content": "Алгоритм обратного распространения вычисляет градиенты по правилу цепочки для обновления параметров сети",
                "concept": "backpropagation",
                "domain": "optimization",
                "mathematical_basis": "chain_rule"
            }
        ]

        for knowledge in semantic_knowledge:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":knowledge["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in knowledge.items() if k != "content"}})
            print(f"  Семантическая память: {knowledge['concept']} - {result}")

        # 5. Демонстрация консолидации памяти
        print(f"\n5. Демонстрация консолидации памяти:")

        # Консолидируем рабочую память в эпизодическую
        consolidation_result = self.working_memory_tool.run({"action":"consolidate",
                                                              "from_type":"working",
                                                              "to_type":"episodic",
                                                              "importance_threshold":0.6})
        print(f"Консолидация рабочей памяти: {consolidation_result}")

        # Кросс-типовой поиск
        print(f"\n6. Кросс-типовой поиск:")

        query = "глубокое обучение CNN"

        # Поиск во всех типах памяти
        memory_tools = [
            ("Рабочая память", self.working_memory_tool),
            ("Эпизодическая память", self.episodic_memory_tool),
            ("Семантическая память", self.semantic_memory_tool),
            ("Перцептивная память", self.perceptual_memory_tool)
        ]

        for memory_name, tool in memory_tools:
            results = tool.run({"action":"search", "query":query, "limit":2})
            print(f"  Поиск в {memory_name}: {results[:80]}...")

        # Получаем статистику всех систем памяти
        print(f"\n7. Общее состояние системы:")

        for memory_name, tool in memory_tools:
            stats = tool.run({"action":"stats"})
            print(f"  {memory_name}: {stats}")

def main():
    """Главная функция"""
    print("🧠 Глубокий анализ четырёх типов памяти")
    print("Подробно рассматривает WorkingMemory, EpisodicMemory, SemanticMemory, PerceptualMemory")
    print("=" * 80)

    try:
        demo = MemoryTypesDeepDive()

        # 1. Демонстрация рабочей памяти
        demo.demonstrate_working_memory()

        # 2. Демонстрация эпизодической памяти
        demo.demonstrate_episodic_memory()

        # 3. Демонстрация семантической памяти
        demo.demonstrate_semantic_memory()

        # 4. Демонстрация перцептивной памяти
        demo.demonstrate_perceptual_memory()

        # 5. Демонстрация взаимодействия памяти
        demo.demonstrate_memory_interactions()

        print("\n" + "=" * 80)
        print("🎉 Глубокий анализ четырёх типов памяти завершён!")
        print("=" * 80)

        print("\n✨ Сводка особенностей типов памяти:")
        print("1. 💭 Рабочая память — быстрое временное хранение, ограниченная ёмкость, автоматическое истечение")
        print("2. 📖 Эпизодическая память — полная запись событий, временная последовательность, богатый контекст")
        print("3. 🧠 Семантическая память — абстрактное хранение знаний, концепции и отношения, семантические рассуждения")
        print("4. 👁️ Перцептивная память — мультимодальная поддержка, кросс-модальный поиск, перцептивное понимание")

        print("\n🔄 Паттерны взаимодействия памяти:")
        print("• Перцептивная → рабочая → эпизодическая → семантическая (поток обработки информации)")
        print("• Семантическая → рабочая (активация и применение знаний)")
        print("• Кросс-типовой поиск и интеграция (интеллектуальное управление памятью)")

        print("\n💡 Ценность проектирования:")
        print("• Моделирование человеческих когнитивных процессов")
        print("• Поддержка многоуровневой обработки информации")
        print("• Реализация интеллектуального управления памятью")
        print("• Обеспечение богатых возможностей поиска")

    except Exception as e:
        print(f"\n❌ Ошибка в процессе демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
