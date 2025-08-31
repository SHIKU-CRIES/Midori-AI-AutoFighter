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
    # Allow battle scaling to respect a lower minimum defense specifically for Slime
    min_defense_override: int = 0

    def __post_init__(self) -> None:
        for f in fields(FoeBase):
            value = getattr(self, f.name)
            if isinstance(value, (int, float)):
                setattr(self, f.name, type(value)(value * 0.1))
        # Make Slime much squishier: apply an extra 10x reduction to defense
        try:
            self.defense = int(self.defense * 0.1)
        except Exception:
            pass
