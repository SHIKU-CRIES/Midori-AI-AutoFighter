from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Graygray(PlayerBase):
    id = "graygray"
    name = "Graygray"
    char_type = CharacterType.B
