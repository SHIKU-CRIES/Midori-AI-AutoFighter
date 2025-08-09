from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class LadyEcho(PlayerBase):
    id = "lady_echo"
    name = "LadyEcho"
    char_type = CharacterType.B
