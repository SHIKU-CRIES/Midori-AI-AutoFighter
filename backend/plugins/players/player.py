from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types.fire import Fire
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase

@dataclass
class Player(PlayerBase):
    id = "player"
    name = "Player"
    char_type = CharacterType.C
    damage_type: DamageTypeBase = field(default_factory=Fire)
    prompt: str = "Player prompt placeholder"
    about: str = "Player description placeholder"
