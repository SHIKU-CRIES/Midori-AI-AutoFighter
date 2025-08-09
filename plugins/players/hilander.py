from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Hilander(PlayerBase):
    id = "hilander"
    name = "Hilander"
    char_type = CharacterType.A
