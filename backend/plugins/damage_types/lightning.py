from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Lightning(DamageTypeBase):
    id = "Lightning"
    weakness = "Wind"
    color = (255, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Charged Decay", int(damage * 0.25), 3, "lightning_dot", source)
