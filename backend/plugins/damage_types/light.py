from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Light(DamageTypeBase):
    id = "Light"
    weakness = "Dark"
    color = (255, 255, 255)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Celestial Atrophy", int(damage * 0.3), 3, "light_dot", source)
