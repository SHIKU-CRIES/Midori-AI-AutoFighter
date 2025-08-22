from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields

from plugins.damage_types import random_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.foes._base import FoeBase


@dataclass
class Slime(FoeBase):
    id = "slime"
    name = "Slime"
    prompt: str = "Foe prompt placeholder"
    about: str = "Foe description placeholder"
    damage_type: DamageTypeBase = field(default_factory=random_damage_type)

    def __post_init__(self) -> None:  # noqa: D401 - short init
        for f in fields(FoeBase):
            value = getattr(self, f.name)
            if isinstance(value, (int, float)):
                setattr(self, f.name, type(value)(value * 0.1))
