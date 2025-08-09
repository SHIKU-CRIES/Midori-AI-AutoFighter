from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Mezzy(PlayerBase):
    id = "mezzy"
    name = "Mezzy"
    char_type = CharacterType.B
