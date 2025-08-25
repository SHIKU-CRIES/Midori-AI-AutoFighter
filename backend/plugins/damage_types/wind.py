from dataclasses import dataclass
from autofighter.effects import DamageOverTime
from plugins import damage_effects
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id: str = "Wind"
    weakness: str = "Lightning"
    color: tuple[int, int, int] = (0, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        return damage_effects.create_dot(self.id, damage, source)
