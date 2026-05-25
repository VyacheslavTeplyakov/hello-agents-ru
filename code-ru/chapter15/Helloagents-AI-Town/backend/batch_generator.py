"""Пакетный генератор диалогов NPC"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional

# Добавляем HelloAgents в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'HelloAgents'))

from hello_agents import HelloAgentsLLM
from agents import NPC_ROLES

class NPCBatchGenerator:
    """Пакетный генератор диалогов NPC

    Идея: один вызов LLM генерирует реплики для всех NPC, чтобы снизить
    стоимость API-вызовов и задержку.
    """

    def __init__(self):
        """Инициализирует пакетный генератор"""
        print("🎨 Инициализирую пакетный генератор диалогов...")

        try:
            self.llm = HelloAgentsLLM()
            self.enabled = True
            print("✅ Пакетный генератор успешно инициализирован")
        except Exception as e:
            print(f"❌ Не удалось инициализировать пакетный генератор: {e}")
            print("⚠️  Будет использоваться режим заготовленных диалогов")
            self.llm = None
            self.enabled = False

        self.npc_configs = NPC_ROLES

        # Заготовленные диалоги (используются, когда LLM недоступен)
        self.preset_dialogues = {
            "morning": {
                "Иван": "Доброе утро! Сегодня продолжу оптимизировать ту мультиагентную систему.",
                "Пётр": "Новый день начался — сначала разберу расписание встреч.",
                "Сергей": "Утро! Сперва чашка кофе для бодрости, потом займусь новым интерфейсом."
            },
            "noon": {
                "Иван": "Всё утро писал код — наконец-то починил тот баг!",
                "Пётр": "Утренний разбор требований прошёл гладко, продолжаем после обеда.",
                "Сергей": "Эта цветовая палитра неплохо смотрится, надо подправить детали."
            },
            "afternoon": {
                "Иван": "После обеда продолжаю писать код, надо ещё оптимизировать этот алгоритм.",
                "Пётр": "Готовлю продуктовое планирование на следующую неделю, документ почти готов.",
                "Сергей": "Дизайн в целом готов, скоро покажу команде."
            },
            "evening": {
                "Иван": "Сегодняшний код закоммитил, завтра продолжу!",
                "Пётр": "Работа на сегодня закончена, надо составить список дел на завтра.",
                "Сергей": "Дизайн на сегодня завершён, завтра ещё доработаю."
            }
        }

    def generate_batch_dialogues(self, context: Optional[str] = None) -> Dict[str, str]:
        """Пакетно генерирует диалоги всех NPC

        Args:
            context: контекст сцены (например, «утренние рабочие часы», «обеденный перерыв» и т.п.)

        Returns:
            Dict[str, str]: соответствие «имя NPC -> реплика»
        """
        if not self.enabled or self.llm is None:
            # Используем заготовленные диалоги
            return self._get_preset_dialogues()

        try:
            # Строим промпт для пакетной генерации
            prompt = self._build_batch_prompt(context)

            # Один вызов LLM — все реплики
            # Используем метод invoke, а не chat
            response = self.llm.invoke([
                {"role": "system", "content": "Ты — генератор диалогов игровых NPC, мастерски создаёшь естественные и живые офисные реплики."},
                {"role": "user", "content": prompt}
            ])

            # Парсим JSON-ответ
            dialogues = self._parse_response(response)

            if dialogues:
                print(f"✅ Пакетная генерация успешна: {len(dialogues)} диалогов NPC")
                return dialogues
            else:
                print("⚠️  Не удалось распарсить ответ, используем заготовленные диалоги")
                return self._get_preset_dialogues()

        except Exception as e:
            print(f"❌ Сбой пакетной генерации: {e}")
            return self._get_preset_dialogues()

    def _build_batch_prompt(self, context: Optional[str] = None) -> str:
        """Собирает промпт для пакетной генерации"""
        # Если контекст не задан, определяем по времени
        if context is None:
            context = self._get_current_context()

        # Описание NPC
        npc_descriptions = []
        for name, cfg in self.npc_configs.items():
            desc = f"- {name} ({cfg['title']}): в локации «{cfg['location']}», занятие — «{cfg['activity']}», характер: {cfg['personality']}"
            npc_descriptions.append(desc)

        npc_desc_text = "\n".join(npc_descriptions)

        prompt = f"""Сгенерируй текущие реплики или описание поведения для трёх NPC из офиса Datawhale.

[Сцена] {context}

[Информация о NPC]
{npc_desc_text}

[Требования]
1. Для каждого NPC — одна фраза (20-40 знаков)
2. Содержание должно соответствовать роли, текущему занятию и атмосфере сцены
3. Это может быть разговор с самим собой, описание рабочего состояния или простая мысль
4. Должно звучать естественно, как у настоящего коллеги
5. Допустимо отражать особенности характера и эмоции
6. **Строго соблюдай формат JSON в ответе**

[Формат вывода] (соблюдай строго)
{{"Иван": "...", "Пётр": "...", "Сергей": "..."}}

[Пример вывода]
{{"Иван": "Этот баг просто магия какая-то, уже два часа дебажу...", "Пётр": "Угу, приоритет этой функции стоит пересмотреть.", "Сергей": "Латте-арт на этой чашке отличный — пришло вдохновение!"}}

Сгенерируй (верни только JSON, без какого-либо другого текста):
"""
        return prompt

    def _parse_response(self, response: str) -> Optional[Dict[str, str]]:
        """Парсит ответ LLM"""
        try:
            # Пробуем распарсить JSON напрямую
            dialogues = json.loads(response)

            # Проверяем формат
            if isinstance(dialogues, dict) and all(name in dialogues for name in self.npc_configs.keys()):
                return dialogues
            else:
                print(f"⚠️  Неверный формат JSON: {dialogues}")
                return None

        except json.JSONDecodeError:
            # Пробуем извлечь JSON-фрагмент
            try:
                # Ищем первую { и последнюю }
                start = response.find('{')
                end = response.rfind('}') + 1

                if start != -1 and end > start:
                    json_str = response[start:end]
                    dialogues = json.loads(json_str)

                    if isinstance(dialogues, dict):
                        return dialogues
            except:
                pass

            print(f"⚠️  Не удалось распарсить ответ: {response[:100]}...")
            return None

    def _get_current_context(self) -> str:
        """Определяет контекст сцены по текущему времени"""
        hour = datetime.now().hour

        if 6 <= hour < 9:
            return "Раннее утро: все постепенно приходят в офис и готовятся к новому дню"
        elif 9 <= hour < 12:
            return "Утренние рабочие часы: все сосредоточены на работе, в офисе деловая, рабочая атмосфера"
        elif 12 <= hour < 14:
            return "Обеденный перерыв: все отдыхают и расслабляются, болтают или смотрят в телефон"
        elif 14 <= hour < 17:
            return "Дневные рабочие часы: продолжают двигать проекты, иногда нужна чашка кофе для бодрости"
        elif 17 <= hour < 19:
            return "Вечернее время: завершают рабочий день и планируют дела на завтра"
        else:
            return "Ночное время: в офисе тихо, изредка кто-то ещё задерживается на работе"

    def _get_preset_dialogues(self) -> Dict[str, str]:
        """Возвращает заготовленные диалоги (по времени суток)"""
        hour = datetime.now().hour

        if 6 <= hour < 12:
            period = "morning"
        elif 12 <= hour < 14:
            period = "noon"
        elif 14 <= hour < 18:
            period = "afternoon"
        else:
            period = "evening"

        return self.preset_dialogues.get(period, self.preset_dialogues["morning"])

# Глобальный экземпляр-синглтон
_batch_generator = None

def get_batch_generator() -> NPCBatchGenerator:
    """Возвращает singleton-экземпляр пакетного генератора"""
    global _batch_generator
    if _batch_generator is None:
        _batch_generator = NPCBatchGenerator()
    return _batch_generator
