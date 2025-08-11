from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Wind(DamageTypeBase):
    id = "Wind"
    weakness = "Lightning"
    color = (0, 255, 0)
