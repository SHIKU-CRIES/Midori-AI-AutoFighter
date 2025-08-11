from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Lightning(DamageTypeBase):
    id = "Lightning"
    weakness = "Wind"
    color = (255, 255, 0)
