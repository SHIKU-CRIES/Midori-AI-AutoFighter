from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class LadyOfFire(PlayerBase):
    id = "lady_of_fire"
    name = "LadyOfFire"
    char_type = CharacterType.B
