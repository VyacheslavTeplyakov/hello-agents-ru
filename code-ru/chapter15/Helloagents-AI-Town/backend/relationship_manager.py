"""Система управления симпатией NPC"""

import sys
import os

# Добавляем HelloAgents в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'HelloAgents'))

from hello_agents import SimpleAgent, HelloAgentsLLM
from typing import Dict, Optional, Tuple
import json
import re

class RelationshipManager:
    """Менеджер симпатии NPC

    Возможности:
    - управляет симпатией NPC к игроку (0-100)
    - использует LLM для анализа эмоций диалога
    - автоматически обновляет уровень симпатии
    - предоставляет уровень отношений и модификаторы стиля
    """

    def __init__(self, llm: HelloAgentsLLM):
        """Инициализирует менеджер симпатии

        Args:
            llm: экземпляр HelloAgentsLLM
        """
        self.llm = llm

        # Хранилище симпатии каждого NPC к каждому игроку
        # Формат: {npc_name: {player_id: affinity_score}}
        self.affinity_scores: Dict[str, Dict[str, float]] = {}

        # Создаём агента анализа симпатии
        self.analyzer_agent = SimpleAgent(
            name="AffinityAnalyzer",
            llm=llm,
            system_prompt=self._create_analyzer_prompt()
        )

        print("💖 Система управления симпатией инициализирована")

    def _create_analyzer_prompt(self) -> str:
        """Создаёт системный промпт для агента анализа эмоций"""
        return """Ты — эксперт по эмоциональному анализу. Твоя задача — анализировать эмоциональную окраску диалога и определять, нужно ли менять симпатию NPC к игроку.

[Задача]
Проанализировать диалог игрока и NPC, определить, нужно ли менять симпатию и насколько.

[Аспекты анализа]
1. **Настрой игрока**: дружелюбный / нейтральный / недружелюбный
2. **Содержание диалога**: позитивное / нейтральное / негативное
3. **Качество взаимодействия**: глубокое / обычное / поверхностное
4. **Эмоциональная окраска**: похвала / критика / нейтральная

[Правила изменения симпатии]
- Похвала, благодарность, просьба об обучении: от +3 до +8
- Дружеское приветствие, обычное общение: от +1 до +3
- Обычная болтовня, нейтральная тема: 0
- Критика, сомнения, раздражение: от -3 до -8
- Оскорбления, агрессия, злонамеренность: от -8 до -15

[Формат вывода] (строгий JSON, без какого-либо другого текста)
{
    "should_change": true/false,
    "change_amount": целое число от -15 до +10,
    "reason": "краткое объяснение причины (до 10 знаков)",
    "sentiment": "positive/neutral/negative"
}

[Пример 1]
Игрок: «Привет, рад познакомиться!»
NPC: «Привет! Я тоже рад знакомству.»
Вывод: {"should_change": true, "change_amount": 5, "reason": "дружеское приветствие", "sentiment": "positive"}

[Пример 2]
Игрок: «Этот дизайн просто ужас!»
NPC: «Извини, я постараюсь исправить...»
Вывод: {"should_change": true, "change_amount": -8, "reason": "критика работы", "sentiment": "negative"}

[Пример 3]
Игрок: «Сегодня хорошая погода»
NPC: «Да, неплохая.»
Вывод: {"should_change": false, "change_amount": 0, "reason": "обычная болтовня", "sentiment": "neutral"}

[Пример 4]
Игрок: «У тебя отличный код!»
NPC: «Спасибо! Сейчас изучаю новые технологии.»
Вывод: {"should_change": true, "change_amount": 8, "reason": "похвала работы", "sentiment": "positive"}

[Пример 5]
Игрок: «Можешь меня научить?»
NPC: «Конечно! С удовольствием поделюсь.»
Вывод: {"should_change": true, "change_amount": 6, "reason": "просьба об обучении", "sentiment": "positive"}

[Важно]
- Выводи только JSON, без объяснений и другого текста
- change_amount должен быть целым числом
- reason должен быть кратким (до 10 знаков)
- sentiment должен быть одним из: positive/neutral/negative
"""

    def get_affinity(self, npc_name: str, player_id: str = "player") -> float:
        """Возвращает симпатию (0-100)

        Args:
            npc_name: имя NPC
            player_id: идентификатор игрока

        Returns:
            значение симпатии (0-100)
        """
        if npc_name not in self.affinity_scores:
            self.affinity_scores[npc_name] = {}

        if player_id not in self.affinity_scores[npc_name]:
            self.affinity_scores[npc_name][player_id] = 50.0  # Стартовая симпатия 50

        return self.affinity_scores[npc_name][player_id]

    def set_affinity(self, npc_name: str, affinity: float, player_id: str = "player"):
        """Устанавливает симпатию

        Args:
            npc_name: имя NPC
            affinity: значение симпатии (0-100)
            player_id: идентификатор игрока
        """
        if npc_name not in self.affinity_scores:
            self.affinity_scores[npc_name] = {}

        # Ограничиваем диапазоном 0-100
        affinity = max(0.0, min(100.0, affinity))
        self.affinity_scores[npc_name][player_id] = affinity

    def analyze_and_update_affinity(
        self,
        npc_name: str,
        player_message: str,
        npc_response: str,
        player_id: str = "player"
    ) -> Dict:
        """Анализирует диалог и обновляет симпатию

        Args:
            npc_name: имя NPC
            player_message: сообщение игрока
            npc_response: ответ NPC
            player_id: идентификатор игрока

        Returns:
            словарь с результатом анализа
        """
        # Готовим промпт для анализа
        prompt = f"""Проанализируй следующий диалог:

Игрок: {player_message}
{npc_name}: {npc_response}

Определи, нужно ли менять симпатию, и укажи величину изменения.
"""

        try:
            # Запускаем агента анализа
            response = self.analyzer_agent.run(prompt)

            # Парсим JSON-ответ
            analysis = self._parse_analysis(response)

            if analysis["should_change"]:
                # Обновляем симпатию
                current_affinity = self.get_affinity(npc_name, player_id)
                new_affinity = current_affinity + analysis["change_amount"]
                new_affinity = max(0.0, min(100.0, new_affinity))  # Ограничиваем 0-100

                self.set_affinity(npc_name, new_affinity, player_id)

                # Получаем уровни симпатии
                old_level = self.get_affinity_level(current_affinity)
                new_level = self.get_affinity_level(new_affinity)

                # Примечание: вывод лога перенесён в agents.py во избежание дублирования

                return {
                    "changed": True,
                    "old_affinity": current_affinity,
                    "new_affinity": new_affinity,
                    "change_amount": analysis["change_amount"],
                    "reason": analysis["reason"],
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "old_level": old_level,
                    "new_level": new_level
                }
            else:
                return {
                    "changed": False,
                    "affinity": self.get_affinity(npc_name, player_id),
                    "reason": analysis["reason"],
                    "sentiment": analysis.get("sentiment", "neutral")
                }

        except Exception as e:
            print(f"❌ Сбой анализа симпатии: {e}")
            import traceback
            traceback.print_exc()
            return {
                "changed": False,
                "affinity": self.get_affinity(npc_name, player_id),
                "reason": "сбой анализа",
                "sentiment": "neutral"
            }

    def _parse_analysis(self, response: str) -> Dict:
        """Парсит результат анализа

        Args:
            response: ответ LLM

        Returns:
            разобранный словарь
        """
        try:
            # Пробуем сразу распарсить JSON
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            # Пробуем вытащить JSON-фрагмент
            # Ищем первую { и последнюю }
            start = response.find('{')
            end = response.rfind('}') + 1

            if start != -1 and end > start:
                json_str = response[start:end]
                try:
                    analysis = json.loads(json_str)
                    return analysis
                except json.JSONDecodeError:
                    pass

            # Пробуем достать поля регулярными выражениями
            # Ищем "should_change": true/false
            should_change_match = re.search(r'"should_change"\s*:\s*(true|false)', response, re.IGNORECASE)
            change_amount_match = re.search(r'"change_amount"\s*:\s*(-?\d+)', response)
            reason_match = re.search(r'"reason"\s*:\s*"([^"]+)"', response)
            sentiment_match = re.search(r'"sentiment"\s*:\s*"([^"]+)"', response)

            if should_change_match and change_amount_match:
                return {
                    "should_change": should_change_match.group(1).lower() == "true",
                    "change_amount": int(change_amount_match.group(1)),
                    "reason": reason_match.group(1) if reason_match else "не указано",
                    "sentiment": sentiment_match.group(1) if sentiment_match else "neutral"
                }

            # Парсинг не удался — возвращаем значения по умолчанию
            print(f"⚠️  Не удалось распарсить JSON, используются значения по умолчанию. Сырой ответ: {response[:100]}...")
            return {
                "should_change": False,
                "change_amount": 0,
                "reason": "сбой парсинга",
                "sentiment": "neutral"
            }

    def get_affinity_level(self, affinity: float) -> str:
        """Возвращает уровень отношений

        Args:
            affinity: значение симпатии (0-100)

        Returns:
            название уровня отношений
        """
        if affinity >= 80:
            return "близкий друг"
        elif affinity >= 60:
            return "близкий"
        elif affinity >= 40:
            return "дружелюбный"
        elif affinity >= 20:
            return "знакомый"
        else:
            return "незнакомец"

    def get_affinity_modifier(self, affinity: float) -> str:
        """Возвращает модификатор симпатии (для адаптации стиля диалога)

        Args:
            affinity: значение симпатии (0-100)

        Returns:
            модификатор стиля диалога
        """
        if affinity >= 80:
            return "очень тёплый и дружелюбный, как со старым другом, готов делиться личным"
        elif affinity >= 60:
            return "дружелюбен и приветлив, охотно беседует, инициативно интересуется собеседником"
        elif affinity >= 40:
            return "вежливо и доброжелательно, обычное общение, сохраняет профессионализм"
        elif affinity >= 20:
            return "вежливо, но слегка отстранённо, ответы краткие"
        else:
            return "холодная отстранённость, мало говорит, ответы лаконичны"

    def get_all_affinities(self, player_id: str = "player") -> Dict[str, Dict]:
        """Возвращает информацию о симпатии всех NPC

        Args:
            player_id: идентификатор игрока

        Returns:
            словарь со значениями симпатии всех NPC
        """
        result = {}
        for npc_name in self.affinity_scores:
            affinity = self.get_affinity(npc_name, player_id)
            result[npc_name] = {
                "affinity": affinity,
                "level": self.get_affinity_level(affinity),
                "modifier": self.get_affinity_modifier(affinity)
            }
        return result
