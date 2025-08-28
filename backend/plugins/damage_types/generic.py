from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Generic(DamageTypeBase):
    id: str = "Generic"
    weakness: str = "none"
    color: tuple[int, int, int] = (255, 255, 255)
