from typing import TYPE_CHECKING
from dataclasses import dataclass

from autofighter.stats import Stats
from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from plugins.dots.blazing_torment import BlazingTorment


@dataclass
class Fire(DamageTypeBase):
    id: str = "Fire"
    weakness: str = "Ice"
    color: tuple[int, int, int] = (255, 0, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        from plugins.dots.blazing_torment import BlazingTorment

        dot = BlazingTorment(int(damage * 0.5), 3)
        dot.source = source
        return dot

    def on_damage(self, damage: float, attacker: Stats, target: Stats) -> float:
        if attacker.max_hp <= 0:
            return damage
        missing_ratio = 1 - (attacker.hp / attacker.max_hp)
        return damage * (1 + missing_ratio)
