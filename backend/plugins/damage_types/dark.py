from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Dark(DamageTypeBase):
    id = "Dark"
    weakness = "Light"
    color = (145, 0, 145)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return DamageOverTime("Abyssal Corruption", int(damage * 0.4), 3, "dark_dot", source)
