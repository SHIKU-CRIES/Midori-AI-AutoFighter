from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Fire(DamageTypeBase):
    id = "Fire"
    weakness = "Ice"
    color = (255, 0, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Blazing Torment", int(damage * 0.5), 3, "fire_dot", source)
