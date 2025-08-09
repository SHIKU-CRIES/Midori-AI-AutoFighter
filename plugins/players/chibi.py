from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Chibi(PlayerBase):
    id = "chibi"
    name = "Chibi"
    char_type = CharacterType.A
