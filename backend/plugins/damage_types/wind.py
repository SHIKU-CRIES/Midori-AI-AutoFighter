from typing import TYPE_CHECKING
from dataclasses import dataclass

from autofighter.effects import DamageOverTime
from plugins.damage_types._base import DamageTypeBase

if TYPE_CHECKING:
    from plugins.dots.gale_erosion import GaleErosion


@dataclass
class Wind(DamageTypeBase):
    id: str = "Wind"
    weakness: str = "Lightning"
    color: tuple[int, int, int] = (0, 255, 0)

    def create_dot(self, damage: float, source) -> DamageOverTime | None:
        from plugins.dots.gale_erosion import GaleErosion

        dot = GaleErosion(int(damage * 0.25), 3)
        dot.source = source
        return dot
