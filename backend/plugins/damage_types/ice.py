from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Ice(DamageTypeBase):
    id = "Ice"
    weakness = "Fire"
    color = (0, 255, 255)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Frozen Wound", int(damage * 0.25), 3, "ice_dot", source)
