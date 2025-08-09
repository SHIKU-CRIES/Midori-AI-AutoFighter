from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Kboshi(PlayerBase):
    id = "kboshi"
    name = "Kboshi"
    char_type = CharacterType.A
