# -*- coding: utf-8 -*-
"""Модели структурированного вывода для игры «Троецарствие: Мафия»"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from agentscope.agent import AgentBase


class DiscussionModelCN(BaseModel):
    """Формат вывода обсуждения"""

    reach_agreement: bool = Field(
        description="Достигнуто ли единое мнение",
    )
    confidence_level: int = Field(
        description="Уровень уверенности в текущей логике (1-10)",
        ge=1, le=10
    )
    key_evidence: Optional[str] = Field(
        description="Ключевые доказательства в поддержку вашей позиции",
        default=None
    )


def get_vote_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """Получить модель голосования"""

    class VoteModelCN(BaseModel):
        """Формат вывода голосования"""

        vote: Literal[tuple(_.name for _ in agents)] = Field(
            description="Имя игрока, за выбывание которого ты голосуешь",
        )
        reason: str = Field(
            description="Причина голосования — краткое объяснение выбора",
        )
        suspicion_level: int = Field(
            description="Уровень подозрения к голосуемому (1-10)",
            ge=1, le=10
        )

    return VoteModelCN


class WitchActionModelCN(BaseModel):
    """Модель действий ведьмы"""

    use_antidote: bool = Field(
        description="Использовать ли противоядие для спасения",
        default=False
    )
    use_poison: bool = Field(
        description="Использовать ли яд для убийства",
        default=False
    )
    target_name: Optional[str] = Field(
        description="Имя целевого игрока (цель спасения или отравления)",
        default=None
    )
    action_reason: Optional[str] = Field(
        description="Причина действия",
        default=None
    )


def get_seer_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """Получить модель провидца"""

    class SeerModelCN(BaseModel):
        """Формат проверки провидца"""

        target: Literal[tuple(_.name for _ in agents)] = Field(
            description="Имя игрока, которого нужно проверить",
        )
        check_reason: str = Field(
            description="Причина выбора этого игрока для проверки",
        )
        priority_level: int = Field(
            description="Приоритет проверки (1-10)",
            ge=1, le=10
        )

    return SeerModelCN


def get_hunter_model_cn(agents: list[AgentBase]) -> type[BaseModel]:
    """Получить модель охотника"""

    class HunterModelCN(BaseModel):
        """Формат выстрела охотника"""

        shoot: bool = Field(
            description="Использовать ли способность выстрела",
        )
        target: Optional[Literal[tuple(_.name for _ in agents)]] = Field(
            description="Имя цели выстрела",
            default=None
        )
        shoot_reason: Optional[str] = Field(
            description="Причина выстрела",
            default=None
        )

    return HunterModelCN


class WerewolfKillModelCN(BaseModel):
    """Модель убийства оборотнем"""

    target: str = Field(
        description="Имя игрока, которого нужно убить",
    )
    kill_strategy: str = Field(
        description="Описание стратегии убийства",
    )
    team_coordination: Optional[str] = Field(
        description="План взаимодействия с другими оборотнями",
        default=None
    )


class GameAnalysisModelCN(BaseModel):
    """Модель анализа игры"""

    suspected_werewolves: List[str] = Field(
        description="Список подозреваемых оборотней",
        default_factory=list
    )
    trusted_players: List[str] = Field(
        description="Список доверенных игроков",
        default_factory=list
    )
    key_clues: List[str] = Field(
        description="Список ключевых улик",
        default_factory=list
    )
    next_strategy: str = Field(
        description="Стратегия на следующий шаг",
    )
