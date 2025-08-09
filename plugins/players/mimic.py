from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Mimic(PlayerBase):
    id = "mimic"
    name = "Mimic"
    char_type = CharacterType.C
