# -*- coding: utf-8 -*-
"""Вспомогательные функции для игры «Троецарствие: Мафия»"""
import asyncio
import random
from typing import List, Dict, Optional, Any
from collections import Counter

from agentscope.agent import AgentBase
from agentscope.message import Msg

# Константы игры
MAX_GAME_ROUND = 10
MAX_DISCUSSION_ROUND = 3
CHINESE_NAMES = [
    "Лю Бэй", "Гуань Юй", "Чжан Фэй", "Чжугэ Лян", "Чжао Юнь",
    "Цао Цао", "Сыма И", "Дянь Вэй", "Сюй Чу", "Ся Хоу Дунь",
    "Сунь Цюань", "Чжоу Юй", "Лу Сюнь", "Гань Нин", "Тайши Цы",
    "Люй Бу", "Дяочань", "Дун Чжо", "Юань Шао", "Юань Шу"
]


def get_chinese_name(character: str = None) -> str:
    """Получить имя персонажа"""
    if character and character in CHINESE_NAMES:
        return character
    return random.choice(CHINESE_NAMES)


def format_player_list(players: List[AgentBase], show_roles: bool = False) -> str:
    """Форматировать список игроков"""
    if not players:
        return "нет игроков"

    if show_roles:
        return ", ".join([f"{p.name}({getattr(p, 'role', 'неизвестно')})" for p in players])
    else:
        return ", ".join([p.name for p in players])


def majority_vote_cn(votes: Dict[str, str]) -> tuple[str, int]:
    """Подсчёт голосов большинства"""
    if not votes:
        return "никто", 0

    vote_counts = Counter(votes.values())
    most_voted = vote_counts.most_common(1)[0]

    return most_voted[0], most_voted[1]


def check_winning_cn(alive_players: List[AgentBase], roles: Dict[str, str]) -> Optional[str]:
    """Проверить условия победы"""
    alive_roles = [roles.get(p.name, "Крестьянин") for p in alive_players]
    werewolf_count = alive_roles.count("Оборотень")
    villager_count = len(alive_roles) - werewolf_count

    if werewolf_count == 0:
        return "Победа команды мирных! Все оборотни устранены!"
    elif werewolf_count >= villager_count:
        return "Победа команды оборотней! Число оборотней достигло или превысило число мирных!"

    return None


def analyze_speech_pattern(speech: str) -> Dict[str, Any]:
    """Анализ паттернов речи"""
    analysis = {
        "word_count": len(speech),
        "confidence_keywords": 0,
        "doubt_keywords": 0,
        "emotion_score": 0
    }

    # Анализ ключевых слов уверенности
    confidence_words = ["точно", "определённо", "обязательно", "абсолютно", "несомненно", "явно"]
    doubt_words = ["возможно", "может быть", "наверное", "подозреваю", "не уверен", "кажется"]

    for word in confidence_words:
        analysis["confidence_keywords"] += speech.count(word)

    for word in doubt_words:
        analysis["doubt_keywords"] += speech.count(word)

    # Простой анализ эмоциональной окраски
    positive_words = ["хорошо", "отлично", "поддерживаю", "согласен", "верно"]
    negative_words = ["плохо", "неверно", "против", "нельзя", "ошибка"]

    for word in positive_words:
        analysis["emotion_score"] += speech.count(word)

    for word in negative_words:
        analysis["emotion_score"] -= speech.count(word)

    return analysis


class GameModerator(AgentBase):
    """Ведущий игры"""

    def __init__(self) -> None:
        super().__init__()
        self.name = "Ведущий"
        self.game_log: List[str] = []

    async def announce(self, content: str) -> Msg:
        """Опубликовать игровое объявление"""
        msg = Msg(
            name=self.name,
            content=f"📢 {content}",
            role="system"
        )
        self.game_log.append(content)
        await self.print(msg)
        return msg

    async def night_announcement(self, round_num: int) -> Msg:
        """Объявление ночной фазы"""
        content = f"🌙 Наступает ночь {round_num}, всем закрыть глаза..."
        return await self.announce(content)

    async def day_announcement(self, round_num: int) -> Msg:
        """Объявление дневной фазы"""
        content = f"☀️ Наступает день {round_num}, все открывают глаза..."
        return await self.announce(content)

    async def death_announcement(self, dead_players: List[str]) -> Msg:
        """Объявление о смерти"""
        if not dead_players:
            content = "Ночь прошла спокойно, никто не погиб."
        else:
            content = f"Прошлой ночью {format_player_list_str(dead_players)} были убиты."
        return await self.announce(content)

    async def vote_result_announcement(self, voted_out: str, vote_count: int) -> Msg:
        """Объявление результатов голосования"""
        content = f"Результат голосования: {voted_out} выбыл с {vote_count} голосами."
        return await self.announce(content)

    async def game_over_announcement(self, winner: str) -> Msg:
        """Объявление об окончании игры"""
        content = f"🎉 Игра завершена! {winner}"
        return await self.announce(content)


def format_player_list_str(players: List[str]) -> str:
    """Форматировать список имён игроков"""
    if not players:
        return "никто"
    return ", ".join(players)


def calculate_suspicion_score(player_name: str, game_history: List[Dict]) -> float:
    """Вычислить индекс подозрительности игрока"""
    score = 0.0

    for event in game_history:
        if event.get("type") == "vote" and event.get("target") == player_name:
            score += 0.3
        elif event.get("type") == "accusation" and event.get("target") == player_name:
            score += 0.2
        elif event.get("type") == "defense" and event.get("player") == player_name:
            score -= 0.1

    return min(max(score, 0.0), 1.0)


async def handle_interrupt(*args: Any, **kwargs: Any) -> Msg:
    """Обработать прерывание игры"""
    return Msg(
        name="Система",
        content="Игра прервана",
        role="system"
    )
