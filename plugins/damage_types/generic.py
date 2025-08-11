from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Generic(DamageTypeBase):
    id = "Generic"
    weakness = "none"
    color = (255, 255, 255)
