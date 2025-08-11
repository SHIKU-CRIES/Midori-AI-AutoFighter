from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Dark(DamageTypeBase):
    id = "Dark"
    weakness = "Light"
    color = (145, 0, 145)
