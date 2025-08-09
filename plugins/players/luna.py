from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Luna(PlayerBase):
    id = "luna"
    name = "Luna"
    char_type = CharacterType.B
