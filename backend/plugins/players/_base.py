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
class PlayerBase(Stats):
    plugin_type = "player"

    hp: int = 1000
    max_hp: int = 1000
    atk: int = 100
    defense: int = 50
    char_type: CharacterType = CharacterType.C
    prompt: str = "Player prompt placeholder"
    about: str = "Player description placeholder"

    exp: int = 1
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1

    crit_rate: float = 0.05
    crit_damage: float = 2
    effect_hit_rate: float = 0.01
    damage_type: DamageTypeBase = field(default_factory=random_damage_type)

    mitigation: int = 100
    regain: int = 1
    dodge_odds: float = 0
    effect_resistance: float = 1.0

    vitality: float = 1.0
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
