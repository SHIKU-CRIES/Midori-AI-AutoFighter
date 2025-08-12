from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Ice(DamageTypeBase):
    id = "Ice"
    weakness = "Fire"
    color = (0, 255, 255)
