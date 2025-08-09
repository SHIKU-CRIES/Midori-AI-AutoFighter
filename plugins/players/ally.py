from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Ally(PlayerBase):
    id = "ally"
    name = "Ally"
    char_type = CharacterType.B
