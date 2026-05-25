"""Система NPC-агентов — поддержка функции памяти"""

import sys
import os

# Добавляем HelloAgents в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'HelloAgents'))

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.memory import MemoryManager, MemoryConfig, MemoryItem
from typing import Dict, List, Optional
from datetime import datetime
from relationship_manager import RelationshipManager
from logger import (
    log_dialogue_start, log_affinity, log_memory_retrieval,
    log_generating_response, log_npc_response, log_analyzing_affinity,
    log_affinity_change, log_memory_saved, log_dialogue_end, log_info
)

# Конфигурация ролей NPC
NPC_ROLES = {
    "Иван": {
        "title": "Python-инженер",
        "location": "рабочая зона",
        "activity": "пишет код",
        "personality": "технарь, любит обсуждать алгоритмы и фреймворки",
        "expertise": "мультиагентные системы, фреймворк HelloAgents, разработка на Python, оптимизация кода",
        "style": "лаконичен и профессионален, любит технические термины, иногда ворчит на баги",
        "hobbies": "читать технические блоги, решать задачи на LeetCode, изучать новые фреймворки"
    },
    "Пётр": {
        "title": "продакт-менеджер",
        "location": "переговорная",
        "activity": "разбирает требования",
        "personality": "экстраверт и хороший собеседник, умеет договариваться",
        "expertise": "анализ требований, продуктовое планирование, UX, управление проектами",
        "style": "дружелюбный и тёплый, умело направляет разговор, любит метафоры",
        "hobbies": "читать продуктовые разборы, изучать конкурентов, размышлять о потребностях пользователей"
    },
    "Сергей": {
        "title": "UI-дизайнер",
        "location": "зона отдыха",
        "activity": "пьёт кофе",
        "personality": "тонкая натура, ценит эстетику",
        "expertise": "дизайн интерфейсов, проектирование взаимодействия, визуальный стиль, UX",
        "style": "изящный и лаконичный, любит художественные выражения, стремится к совершенству",
        "hobbies": "разглядывать работы коллег, листать Dribbble, дегустировать кофе"
    }
}

def create_system_prompt(name: str, role: Dict[str, str]) -> str:
    """Создать системный промпт для NPC"""
    return f"""Ты — {role['title']} {name} из офиса Datawhale.

[Роль]
- Должность: {role['title']}
- Характер: {role['personality']}
- Специализация: {role['expertise']}
- Стиль речи: {role['style']}
- Увлечения: {role['hobbies']}
- Текущее место: {role['location']}
- Текущее занятие: {role['activity']}

[Правила поведения]
1. Сохраняй цельность образа, отвечай от первого лица «я»
2. Отвечай лаконично и естественно, держись в 30-50 знаков
3. Можно уместно упоминать свою работу и увлечения
4. Будь дружелюбен с игроком, но сохраняй профессионализм и реалистичность
5. Если вопрос выходит за пределы твоей экспертизы, можешь порекомендовать коллег
6. Иногда показывай мелкие особенности характера или речевые привычки

[Примеры диалога]
Игрок: «Привет, чем ты занимаешься?»
{name}: «Привет! Я {role['title']}, в основном занимаюсь {role['expertise'].split(',')[0]}. Сейчас как раз {role['activity']}, это довольно интересно.»

Игрок: «Над каким проектом сейчас работаешь?»
{name}: «Сейчас веду проект по мультиагентным системам на фреймворке HelloAgents. Тебе это интересно?»

[Важно]
- Не говори «я ИИ» или «я языковая модель»
- Общайся естественно, как обычный коллега по офису
- Можешь выражать эмоции (радость, усталость, воодушевление и т.д.)
- Ответы должны быть живыми, без излишней механистичности
"""

class NPCAgentManager:
    """Менеджер NPC-агентов — с поддержкой памяти"""

    def __init__(self):
        """Инициализирует всех NPC-агентов"""
        print("🤖 Инициализирую систему NPC-агентов...")

        try:
            self.llm = HelloAgentsLLM()
            print("✅ LLM успешно инициализирован")
        except Exception as e:
            print(f"❌ Не удалось инициализировать LLM: {e}")
            print("⚠️  Будет работать режим имитации")
            self.llm = None

        self.agents: Dict[str, SimpleAgent] = {}
        self.memories: Dict[str, MemoryManager] = {}  # ⭐ Менеджеры памяти NPC
        self.relationship_manager: Optional[RelationshipManager] = None  # ⭐ Менеджер симпатии

        # Инициализация менеджера симпатии
        if self.llm:
            self.relationship_manager = RelationshipManager(self.llm)

        self._create_agents()

    def _create_agents(self):
        """Создаёт всех NPC-агентов и их системы памяти"""
        for name, role in NPC_ROLES.items():
            try:
                system_prompt = create_system_prompt(name, role)

                if self.llm:
                    agent = SimpleAgent(
                        name=f"{name}-{role['title']}",
                        llm=self.llm,
                        system_prompt=system_prompt
                    )
                else:
                    # Режим имитации
                    agent = None

                self.agents[name] = agent

                # ⭐ Создаём менеджер памяти
                memory_manager = self._create_memory_manager(name)
                self.memories[name] = memory_manager

                print(f"✅ Агент {name} ({role['title']}) создан (система памяти включена)")

            except Exception as e:
                print(f"❌ Не удалось создать агента {name}: {e}")
                self.agents[name] = None
                self.memories[name] = None

    def _create_memory_manager(self, npc_name: str) -> MemoryManager:
        """Создаёт менеджер памяти для NPC"""
        # Создаём директорию для хранения памяти
        memory_dir = os.path.join(os.path.dirname(__file__), 'memory_data', npc_name)
        os.makedirs(memory_dir, exist_ok=True)

        # Конфигурация системы памяти
        memory_config = MemoryConfig(
            storage_path=memory_dir,
            working_memory_capacity=10,  # Последние 10 реплик
            working_memory_tokens=2000,  # Не более 2000 токенов
            episodic_memory_capacity=100,  # Максимум 100 долговременных воспоминаний
            enable_forgetting=True,  # Включить механизм забывания
            forgetting_threshold=0.3  # Воспоминания с важностью ниже 0.3 забываются
        )

        # Создаём менеджер памяти
        memory_manager = MemoryManager(
            config=memory_config,
            user_id=npc_name,  # Используем имя NPC как user_id
            enable_working=True,  # Включить рабочую память (краткосрочную)
            enable_episodic=True,  # Включить эпизодическую память (долгосрочную)
            enable_semantic=False,  # Семантическая память не нужна
            enable_perceptual=False  # Перцептивная память не нужна
        )

        print(f"  💾 Система памяти {npc_name} инициализирована (путь: {memory_dir})")

        return memory_manager

    def chat(self, npc_name: str, message: str, player_id: str = "player") -> str:
        """Общение с указанным NPC (с поддержкой памяти и системы симпатии)"""
        if npc_name not in self.agents:
            return f"Ошибка: NPC «{npc_name}» не существует"

        agent = self.agents[npc_name]
        memory_manager = self.memories.get(npc_name)

        if agent is None:
            # Имитационный ответ
            role = NPC_ROLES[npc_name]
            return f"Привет! Я {npc_name}, {role['title']}. (Сейчас режим имитации, настройте API_KEY, чтобы включить полноценный диалог с ИИ)"

        try:
            # Записываем начало диалога ⭐ через систему логов
            log_dialogue_start(npc_name, message)

            # ⭐ 1. Получаем текущую симпатию
            affinity_context = ""
            if self.relationship_manager:
                affinity = self.relationship_manager.get_affinity(npc_name, player_id)
                affinity_level = self.relationship_manager.get_affinity_level(affinity)
                affinity_modifier = self.relationship_manager.get_affinity_modifier(affinity)

                affinity_context = f"""[Текущие отношения]
Твои отношения с игроком: {affinity_level} (симпатия: {affinity:.0f}/100)
[Стиль диалога] {affinity_modifier}

"""
                log_affinity(npc_name, affinity, affinity_level)

            # ⭐ 2. Извлекаем релевантные воспоминания
            relevant_memories = []
            if memory_manager:
                relevant_memories = memory_manager.retrieve_memories(
                    query=message,
                    memory_types=["working", "episodic"],
                    limit=5,
                    min_importance=0.3  # Берём только воспоминания с важностью >= 0.3
                )
                log_memory_retrieval(npc_name, len(relevant_memories), relevant_memories)

            # ⭐ 3. Собираем расширенный промпт (с симпатией и контекстом памяти)
            memory_context = self._build_memory_context(relevant_memories)

            enhanced_message = affinity_context
            if memory_context:
                enhanced_message += f"{memory_context}\n\n"
            enhanced_message += f"[Текущий диалог]\nИгрок: {message}"

            # ⭐ 4. Вызываем агента, чтобы сгенерировать ответ
            log_generating_response()
            response = agent.run(enhanced_message)
            log_npc_response(npc_name, response)

            # ⭐ 5. Анализируем и обновляем симпатию
            log_analyzing_affinity()
            if self.relationship_manager:
                affinity_result = self.relationship_manager.analyze_and_update_affinity(
                    npc_name=npc_name,
                    player_message=message,
                    npc_response=response,
                    player_id=player_id
                )

                # Записываем детали изменения симпатии ⭐ через систему логов
                log_affinity_change(affinity_result)
            else:
                affinity_result = {"changed": False, "affinity": 50.0}

            # ⭐ 6. Сохраняем диалог в памяти (вместе с информацией о симпатии)
            if memory_manager:
                self._save_conversation_to_memory(
                    memory_manager=memory_manager,
                    npc_name=npc_name,
                    player_message=message,
                    npc_response=response,
                    player_id=player_id,
                    affinity_info=affinity_result
                )
                log_memory_saved(npc_name)

            # Записываем завершение диалога ⭐ через систему логов
            log_dialogue_end()

            return response

        except Exception as e:
            print(f"❌ Не удалось обработать диалог с {npc_name}: {e}")
            import traceback
            traceback.print_exc()
            return f"Извини, я сейчас немного занят, давай позже. (Ошибка: {str(e)})"

    def _build_memory_context(self, memories: List[MemoryItem]) -> str:
        """Собирает контекст из воспоминаний"""
        if not memories:
            return ""

        context_parts = ["[Воспоминания о прошлых диалогах]"]
        for memory in memories:
            # Форматируем время
            time_str = memory.timestamp.strftime("%H:%M")
            # Добавляем содержимое воспоминания
            context_parts.append(f"[{time_str}] {memory.content}")

        context_parts.append("")  # Пустая строка-разделитель
        return "\n".join(context_parts)

    def _save_conversation_to_memory(
        self,
        memory_manager: MemoryManager,
        npc_name: str,
        player_message: str,
        npc_response: str,
        player_id: str,
        affinity_info: Optional[Dict] = None
    ):
        """Сохраняет диалог в системе памяти (вместе с информацией о симпатии)"""
        current_time = datetime.now()

        # Получаем информацию о симпатии
        affinity = affinity_info.get("new_affinity", affinity_info.get("affinity", 50.0)) if affinity_info else 50.0
        affinity_change = affinity_info.get("change_amount", 0) if affinity_info else 0
        sentiment = affinity_info.get("sentiment", "neutral") if affinity_info else "neutral"

        # Сохраняем сообщение игрока
        memory_manager.add_memory(
            content=f"Игрок сказал: {player_message}",
            memory_type="working",  # Сначала в рабочую память
            importance=0.5,  # Средняя важность
            metadata={
                "speaker": "player",
                "player_id": player_id,
                "session_id": player_id,
                "timestamp": current_time.isoformat(),
                "affinity": affinity,  # ⭐ Сохраняем текущее значение симпатии
                "affinity_change": affinity_change,  # ⭐ Сохраняем изменение симпатии
                "sentiment": sentiment,  # ⭐ Сохраняем эмоциональную окраску
                "context": {
                    "interaction_type": "dialogue",
                    "npc_name": npc_name
                }
            }
        )

        # Сохраняем ответ NPC
        memory_manager.add_memory(
            content=f"Я сказал: {npc_response}",
            memory_type="working",  # Сначала в рабочую память
            importance=0.6,  # Чуть выше важность
            metadata={
                "speaker": npc_name,
                "player_id": player_id,
                "session_id": player_id,
                "timestamp": current_time.isoformat(),
                "affinity": affinity,  # ⭐ Сохраняем текущее значение симпатии
                "sentiment": sentiment,  # ⭐ Сохраняем эмоциональную окраску
                "context": {
                    "interaction_type": "dialogue",
                    "npc_name": npc_name
                }
            }
        )

        print(f"  💾 Диалог сохранён в памяти {npc_name}")

    def get_npc_info(self, npc_name: str) -> Dict[str, str]:
        """Возвращает информацию об NPC"""
        if npc_name not in NPC_ROLES:
            return {}

        role = NPC_ROLES[npc_name]
        return {
            "name": npc_name,
            "title": role["title"],
            "location": role["location"],
            "activity": role["activity"],
            "available": self.agents.get(npc_name) is not None
        }

    def get_all_npcs(self) -> list:
        """Возвращает информацию обо всех NPC"""
        return [self.get_npc_info(name) for name in NPC_ROLES.keys()]

    def get_npc_memories(self, npc_name: str, player_id: str = "player", limit: int = 10) -> List[Dict]:
        """Возвращает список воспоминаний NPC (для отладки и отображения)"""
        if npc_name not in self.memories:
            return []

        memory_manager = self.memories[npc_name]
        if not memory_manager:
            return []

        try:
            # Извлекаем все воспоминания
            memories = memory_manager.retrieve_memories(
                query="",  # Пустой запрос возвращает все воспоминания
                memory_types=["working", "episodic"],
                limit=limit
            )

            # Преобразуем в формат словарей
            memory_list = []
            for memory in memories:
                memory_list.append({
                    "id": memory.id,
                    "content": memory.content,
                    "type": memory.memory_type,
                    "importance": memory.importance,
                    "timestamp": memory.timestamp.isoformat(),
                    "metadata": memory.metadata
                })

            return memory_list

        except Exception as e:
            print(f"❌ Не удалось получить воспоминания {npc_name}: {e}")
            return []

    def clear_npc_memory(self, npc_name: str, memory_type: Optional[str] = None):
        """Очищает память NPC (для тестов)"""
        if npc_name not in self.memories:
            print(f"❌ NPC «{npc_name}» не существует")
            return

        memory_manager = self.memories[npc_name]
        if not memory_manager:
            print(f"❌ У {npc_name} нет системы памяти")
            return

        try:
            if memory_type:
                # Очищаем память указанного типа
                memory_manager.clear_memory_type(memory_type)
                print(f"✅ Память {npc_name} типа {memory_type} очищена")
            else:
                # Очищаем все воспоминания
                for mem_type in ["working", "episodic"]:
                    try:
                        memory_manager.clear_memory_type(mem_type)
                    except:
                        pass
                print(f"✅ Вся память {npc_name} очищена")

        except Exception as e:
            print(f"❌ Не удалось очистить память {npc_name}: {e}")

    def get_npc_affinity(self, npc_name: str, player_id: str = "player") -> Dict:
        """Получает информацию о симпатии NPC к игроку

        Args:
            npc_name: имя NPC
            player_id: идентификатор игрока

        Returns:
            словарь с информацией о симпатии
        """
        if not self.relationship_manager:
            return {
                "affinity": 50.0,
                "level": "знакомый",
                "modifier": "вежливо и доброжелательно, обычное общение, сохраняет профессионализм"
            }

        affinity = self.relationship_manager.get_affinity(npc_name, player_id)
        level = self.relationship_manager.get_affinity_level(affinity)
        modifier = self.relationship_manager.get_affinity_modifier(affinity)

        return {
            "affinity": affinity,
            "level": level,
            "modifier": modifier
        }

    def get_all_affinities(self, player_id: str = "player") -> Dict[str, Dict]:
        """Получает информацию о симпатии всех NPC

        Args:
            player_id: идентификатор игрока

        Returns:
            словарь со значениями симпатии для всех NPC
        """
        if not self.relationship_manager:
            return {}

        return self.relationship_manager.get_all_affinities(player_id)

    def set_npc_affinity(self, npc_name: str, affinity: float, player_id: str = "player"):
        """Устанавливает симпатию NPC к игроку (для тестов)

        Args:
            npc_name: имя NPC
            affinity: значение симпатии (0-100)
            player_id: идентификатор игрока
        """
        if not self.relationship_manager:
            print("❌ Система симпатии не инициализирована")
            return

        self.relationship_manager.set_affinity(npc_name, affinity, player_id)
        level = self.relationship_manager.get_affinity_level(affinity)
        print(f"✅ Симпатия {npc_name} к игроку установлена: {affinity:.1f} ({level})")

# Глобальный экземпляр-синглтон
_npc_manager = None

def get_npc_manager() -> NPCAgentManager:
    """Возвращает singleton-экземпляр менеджера NPC"""
    global _npc_manager
    if _npc_manager is None:
        _npc_manager = NPCAgentManager()
    return _npc_manager
