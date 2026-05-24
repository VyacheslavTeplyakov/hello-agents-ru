# -*- coding: utf-8 -*-
"""
Троецарствие: Мафия — игра на русском языке на основе AgentScope
Сочетает персонажей «Романа о Трёх Царствах» с классическими правилами мафии
"""
import asyncio
import os
import random
from typing import List, Dict, Optional

from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel
from agentscope.pipeline import MsgHub, sequential_pipeline, fanout_pipeline
from agentscope.formatter import DashScopeMultiAgentFormatter

from prompt_cn import ChinesePrompts
from game_roles import GameRoles
from structured_output_cn import (
    DiscussionModelCN,
    get_vote_model_cn,
    WitchActionModelCN,
    get_seer_model_cn,
    get_hunter_model_cn,
    WerewolfKillModelCN
)
from utils_cn import (
    check_winning_cn,
    majority_vote_cn,
    get_chinese_name,
    format_player_list,
    GameModerator,
    MAX_GAME_ROUND,
    MAX_DISCUSSION_ROUND,
)


class ThreeKingdomsWerewolfGame:
    """Основной класс игры «Троецарствие: Мафия»"""

    def __init__(self):
        self.players: Dict[str, ReActAgent] = {}
        self.roles: Dict[str, str] = {}
        self.moderator = GameModerator()
        self.alive_players: List[ReActAgent] = []
        self.werewolves: List[ReActAgent] = []
        self.villagers: List[ReActAgent] = []
        self.seer: List[ReActAgent] = []
        self.witch: List[ReActAgent] = []
        self.hunter: List[ReActAgent] = []

        # Состояние снадобий ведьмы
        self.witch_has_antidote = True
        self.witch_has_poison = True

    async def create_player(self, role: str, character: str) -> ReActAgent:
        """Создать игрока с персонажем из «Троецарствия»"""
        name = get_chinese_name(character)
        self.roles[name] = role

        agent = ReActAgent(
            name=name,
            sys_prompt=ChinesePrompts.get_role_prompt(role, character),
            model=DashScopeChatModel(
                model_name="qwen-max",
                api_key=os.environ["DASHSCOPE_API_KEY"],
                enable_thinking=True,
            ),
            formatter=DashScopeMultiAgentFormatter(),
        )

        # Подтверждение роли
        await agent.observe(
            await self.moderator.announce(
                f"[{name}] В этой игре «Троецарствие: Мафия» ты играешь роль {GameRoles.get_role_desc(role)}, "
                f"твой персонаж — {character}. {GameRoles.get_role_ability(role)}"
            )
        )

        self.players[name] = agent
        return agent

    async def setup_game(self, player_count: int = 6):
        """Настроить игру"""
        print("🎮 Начало настройки игры «Троецарствие: Мафия»...")

        # Получить набор ролей
        roles = GameRoles.get_standard_setup(player_count)
        characters = random.sample([
            "Лю Бэй", "Гуань Юй", "Чжан Фэй", "Чжугэ Лян", "Чжао Юнь",
            "Цао Цао", "Сыма И", "Чжоу Юй", "Сунь Цюань"
        ], player_count)

        # Создать игроков
        for i, (role, character) in enumerate(zip(roles, characters)):
            agent = await self.create_player(role, character)
            self.alive_players.append(agent)

            # Распределить по командам
            if role == "Оборотень":
                self.werewolves.append(agent)
            elif role == "Провидец":
                self.seer.append(agent)
            elif role == "Ведьма":
                self.witch.append(agent)
            elif role == "Охотник":
                self.hunter.append(agent)
            else:
                self.villagers.append(agent)

        # Объявление о начале игры
        await self.moderator.announce(
            f"Игра «Троецарствие: Мафия» начинается! Участники: {format_player_list(self.alive_players)}"
        )

        print(f"✅ Настройка завершена, всего игроков: {len(self.alive_players)}")

    async def werewolf_phase(self, round_num: int):
        """Фаза оборотней"""
        if not self.werewolves:
            return None

        await self.moderator.announce(f"🐺 Оборотни открывают глаза, выбирают цель на эту ночь...")

        # Обсуждение оборотней
        async with MsgHub(
            self.werewolves,
            enable_auto_broadcast=True,
            announcement=await self.moderator.announce(
                f"Оборотни, обсудите цель убийства на эту ночь. Живые игроки: {format_player_list(self.alive_players)}"
            ),
        ) as werewolves_hub:
            # Фаза обсуждения
            for _ in range(MAX_DISCUSSION_ROUND):
                for wolf in self.werewolves:
                    await wolf(structured_model=DiscussionModelCN)

            # Голосование за убийство
            werewolves_hub.set_auto_broadcast(False)
            kill_votes = await fanout_pipeline(
                self.werewolves,
                msg=await self.moderator.announce("Выберите цель для убийства"),
                structured_model=WerewolfKillModelCN,
                enable_gather=False,
            )

            # Подсчёт голосов
            votes = {}
            for i, vote_msg in enumerate(kill_votes):
                # Проверить, не равен ли vote_msg None и есть ли metadata
                if vote_msg is not None and hasattr(vote_msg, 'metadata') and vote_msg.metadata is not None:
                    votes[self.werewolves[i].name] = vote_msg.metadata.get("target")
                else:
                    # Если результат недействителен — выбрать цель случайно
                    print(f"⚠️ Голос оборотня {self.werewolves[i].name} недействителен, цель выбирается случайно")
                    import random
                    valid_targets = [p.name for p in self.alive_players if p.name not in [w.name for w in self.werewolves]]
                    votes[self.werewolves[i].name] = random.choice(valid_targets) if valid_targets else None

            killed_player, _ = majority_vote_cn(votes)
            return killed_player

    async def seer_phase(self):
        """Фаза провидца"""
        if not self.seer:
            return

        seer_agent = self.seer[0]
        await self.moderator.announce("🔮 Провидец открывает глаза, выбирает игрока для проверки...")

        check_result = await seer_agent(
            structured_model=get_seer_model_cn(self.alive_players)
        )

        # Проверить, действителен ли результат
        if check_result is None or not hasattr(check_result, 'metadata') or check_result.metadata is None:
            print(f"⚠️ Проверка провидца не удалась, этап пропускается")
            return

        target_name = check_result.metadata.get("target")
        if not target_name:
            print(f"⚠️ Провидец не выбрал цель, этап пропускается")
            return

        target_role = self.roles.get(target_name, "Крестьянин")

        # Сообщить провидцу результат
        result_msg = f"Результат проверки: {target_name} является {'оборотнем' if target_role == 'Оборотень' else 'мирным'}"
        await seer_agent.observe(await self.moderator.announce(result_msg))

    async def witch_phase(self, killed_player: str):
        """Фаза ведьмы"""
        if not self.witch:
            return killed_player, None

        witch_agent = self.witch[0]
        await self.moderator.announce("🧙‍♀️ Ведьма открывает глаза...")

        # Сообщить ведьме о смертях
        death_info = f"Сегодня ночью {killed_player} был убит оборотнями" if killed_player else "Эта ночь прошла спокойно"
        await witch_agent.observe(await self.moderator.announce(death_info))

        # Действие ведьмы
        witch_action = await witch_agent(structured_model=WitchActionModelCN)

        saved_player = None
        poisoned_player = None

        # Проверить, действителен ли результат
        if witch_action is None or not hasattr(witch_action, 'metadata') or witch_action.metadata is None:
            print(f"⚠️ Действие ведьмы не удалось, способности не используются")
        else:
            if witch_action.metadata.get("use_antidote") and self.witch_has_antidote:
                if killed_player:
                    saved_player = killed_player
                    self.witch_has_antidote = False
                    await witch_agent.observe(await self.moderator.announce(f"Ты использовала противоядие и спасла {killed_player}"))

            if witch_action.metadata.get("use_poison") and self.witch_has_poison:
                poisoned_player = witch_action.metadata.get("target_name")
                if poisoned_player:
                    self.witch_has_poison = False
                    await witch_agent.observe(await self.moderator.announce(f"Ты использовала яд и отравила {poisoned_player}"))

        # Определить итоговых погибших
        final_killed = killed_player if not saved_player else None

        return final_killed, poisoned_player

    async def hunter_phase(self, shot_by_hunter: str):
        """Фаза охотника"""
        if not self.hunter:
            return None

        hunter_agent = self.hunter[0]
        if hunter_agent.name == shot_by_hunter:
            await self.moderator.announce("🏹 Охотник применяет способность — может забрать с собой одного игрока...")

            hunter_action = await hunter_agent(
                structured_model=get_hunter_model_cn(self.alive_players)
            )

            # Проверить, действителен ли результат
            if hunter_action is None or not hasattr(hunter_action, 'metadata') or hunter_action.metadata is None:
                print(f"⚠️ Способность охотника не сработала, выстрел отменяется")
                return None

            if hunter_action.metadata.get("shoot"):
                target = hunter_action.metadata.get("target")
                if target:
                    await self.moderator.announce(f"Охотник {hunter_agent.name} выстрелил и забрал с собой {target}")
                    return target
                else:
                    print(f"⚠️ Охотник выбрал выстрел, но не указал цель, выстрел отменяется")
                    return None

        return None

    def update_alive_players(self, dead_players: List[str]):
        """Обновить список живых игроков"""
        for dead_name in dead_players:
            if dead_name:
                # Убрать из списка живых
                self.alive_players = [p for p in self.alive_players if p.name != dead_name]
                # Убрать из команд
                self.werewolves = [p for p in self.werewolves if p.name != dead_name]
                self.villagers = [p for p in self.villagers if p.name != dead_name]
                self.seer = [p for p in self.seer if p.name != dead_name]
                self.witch = [p for p in self.witch if p.name != dead_name]
                self.hunter = [p for p in self.hunter if p.name != dead_name]

    async def day_phase(self, round_num: int):
        """Дневная фаза"""
        await self.moderator.day_announcement(round_num)

        # Фаза обсуждения
        async with MsgHub(
            self.alive_players,
            enable_auto_broadcast=True,
            announcement=await self.moderator.announce(
                f"Начинается свободное обсуждение. Живые игроки: {format_player_list(self.alive_players)}"
            ),
        ) as all_hub:
            # Каждый высказывается по одному разу
            await sequential_pipeline(self.alive_players)

            # Фаза голосования
            all_hub.set_auto_broadcast(False)
            vote_msgs = await fanout_pipeline(
                self.alive_players,
                await self.moderator.announce("Проголосуйте за игрока, которого хотите исключить"),
                structured_model=get_vote_model_cn(self.alive_players),
                enable_gather=False,
            )

            # Подсчёт голосов
            votes = {}
            for i, vote_msg in enumerate(vote_msgs):
                # Проверить, не равен ли vote_msg None и есть ли metadata
                if vote_msg is not None and hasattr(vote_msg, 'metadata') and vote_msg.metadata is not None:
                    votes[self.alive_players[i].name] = vote_msg.metadata.get("vote")
                else:
                    # Если результат недействителен — воздержаться
                    print(f"⚠️ Голос игрока {self.alive_players[i].name} недействителен, засчитывается воздержание")
                    votes[self.alive_players[i].name] = None

            voted_out, vote_count = majority_vote_cn(votes)
            await self.moderator.vote_result_announcement(voted_out, vote_count)

            return voted_out

    async def run_game(self):
        """Запустить основной игровой цикл"""
        try:
            await self.setup_game()

            for round_num in range(1, MAX_GAME_ROUND + 1):
                print(f"\n🌙 === Начинается раунд {round_num} ===")

                # Ночная фаза
                await self.moderator.night_announcement(round_num)

                # Убийство оборотнями
                killed_player = await self.werewolf_phase(round_num)

                # Проверка провидца
                await self.seer_phase()

                # Действие ведьмы
                final_killed, poisoned_player = await self.witch_phase(killed_player)

                # Обновить погибших
                night_deaths = [p for p in [final_killed, poisoned_player] if p]
                self.update_alive_players(night_deaths)

                # Объявление о смертях
                await self.moderator.death_announcement(night_deaths)

                # Проверить условия победы
                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                # Дневная фаза
                voted_out = await self.day_phase(round_num)

                # Способность охотника
                hunter_shot = await self.hunter_phase(voted_out)

                # Обновить погибших
                day_deaths = [p for p in [voted_out, hunter_shot] if p]
                self.update_alive_players(day_deaths)

                # Проверить условия победы
                winner = check_winning_cn(self.alive_players, self.roles)
                if winner:
                    await self.moderator.game_over_announcement(winner)
                    return

                print(f"Раунд {round_num} завершён, живые игроки: {format_player_list(self.alive_players)}")

        except Exception as e:
            print(f"❌ Ошибка в ходе игры: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Главная функция"""
    # Проверить переменную окружения
    if "DASHSCOPE_API_KEY" not in os.environ:
        print("❌ Установите переменную окружения DASHSCOPE_API_KEY")
        return

    print("🎮 Добро пожаловать в «Троецарствие: Мафия»!")

    # Создать и запустить игру
    game = ThreeKingdomsWerewolfGame()
    await game.run_game()


if __name__ == "__main__":
    asyncio.run(main())
