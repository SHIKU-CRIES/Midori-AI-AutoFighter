from __future__ import annotations

import logging

from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import Stats
from autofighter.character import CharacterType
from plugins.damage_types import random_damage_type
from plugins.damage_types._base import DamageTypeBase


log = logging.getLogger(__name__)


@dataclass
class FoeBase(Stats):
    plugin_type = "foe"

    hp: int = 1000
    max_hp: int = 1000
    atk: int = 100
    defense: int = 50
    gold: int = 1
    char_type: CharacterType = CharacterType.C
    prompt: str = "Foe prompt placeholder"
    about: str = "Foe description placeholder"

    exp: int = 1
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    crit_rate: float = 0.05
    crit_damage: float = 2
    effect_hit_rate: float = 0.01
    damage_type: DamageTypeBase = field(default_factory=random_damage_type)

    mitigation: float = 0.001
    regain: int = 1
    dodge_odds: float = 0
    effect_resistance: float = 1.0

    vitality: float = 0.001
    action_points: int = 1
    damage_taken: int = 1
    damage_dealt: int = 1
    kills: int = 1

    last_damage_taken: int = 1

    passives: list[str] = field(default_factory=list)
    dots: list[str] = field(default_factory=list)
    hots: list[str] = field(default_factory=list)

    stat_gain_map: dict[str, str] = field(default_factory=dict)
    stat_loss_map: dict[str, str] = field(default_factory=dict)

    def adjust_stat_on_gain(self, stat_name: str, amount: int) -> None:
        target = self.stat_gain_map.get(stat_name, stat_name)
        log.debug(
            "%s gaining %s: %s",
            getattr(self, "id", type(self).__name__),
            target,
            amount,
        )
        super().adjust_stat_on_gain(target, amount)

    def adjust_stat_on_loss(self, stat_name: str, amount: int) -> None:
        target = self.stat_loss_map.get(stat_name, stat_name)
        log.debug(
            "%s losing %s: %s",
            getattr(self, "id", type(self).__name__),
            target,
            amount,
        )
        super().adjust_stat_on_loss(target, amount)

    async def maybe_regain(self, turn: int) -> None:  # noqa: D401
        """Regain a fraction of HP every other turn."""
        if turn % 2 != 0:
            return
        bonus = max(self.regain - 100, 0) * 0.00005
        percent = (0.01 + bonus) / 100
        heal = int(self.max_hp * percent)
        log.debug(
            "%s regains %s HP on turn %s",
            getattr(self, "id", type(self).__name__),
            heal,
            turn,
        )
        await self.apply_healing(heal)

    def _on_level_up(self) -> None:  # noqa: D401
        """Apply base bonuses then boost mitigation and vitality."""
        log.info(
            "%s leveled up to %s",
            getattr(self, "id", type(self).__name__),
            self.level + 1,
        )
        super()._on_level_up()
        self.adjust_stat_on_gain("mitigation", 0.0001)
        self.adjust_stat_on_gain("vitality", 0.0001)
