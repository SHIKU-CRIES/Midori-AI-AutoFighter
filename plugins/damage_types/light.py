from dataclasses import dataclass

from plugins.damage_types._base import DamageTypeBase


@dataclass
class Light(DamageTypeBase):
    id = "Light"
    weakness = "Dark"
    color = (255, 255, 255)
