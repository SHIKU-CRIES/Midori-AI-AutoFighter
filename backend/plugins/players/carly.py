from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Carly(PlayerBase):
    id = "carly"
    name = "Carly"
    char_type = CharacterType.B
    base_damage_type: str = "Light"

