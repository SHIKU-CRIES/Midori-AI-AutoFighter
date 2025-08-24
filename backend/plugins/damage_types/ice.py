from typing import TYPE_CHECKING
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from plugins.dots.frozen_wound import FrozenWound


@dataclass
class Ice(DamageTypeBase):
    id: str = "Ice"
    weakness: str = "Fire"
    color: tuple[int, int, int] = (0, 255, 255)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        from plugins.dots.frozen_wound import FrozenWound

        dot = FrozenWound(int(damage * 0.25), 3)
        dot.source = source
        return dot
