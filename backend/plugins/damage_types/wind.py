from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.dots.gale_erosion import GaleErosion
from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id: str = "Wind"
    weakness: str = "Lightning"
    color: tuple[int, int, int] = (0, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        dot = GaleErosion(int(damage * 0.25), 3)
        dot.source = source
        return dot
