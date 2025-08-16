from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id = "Wind"
    weakness = "Lightning"
    color = (0, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Gale Erosion", int(damage * 0.25), 3, "wind_dot", source)
