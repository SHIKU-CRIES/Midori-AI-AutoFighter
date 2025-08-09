from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class LadyDarkness(PlayerBase):
    id = "lady_darkness"
    name = "LadyDarkness"
    char_type = CharacterType.B
