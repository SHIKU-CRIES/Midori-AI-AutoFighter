from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Fire(DamageTypeBase):
    id = "Fire"
    weakness = "Ice"
    color = (255, 0, 0)
