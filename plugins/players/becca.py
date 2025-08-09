from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Becca(PlayerBase):
    id = "becca"
    name = "Becca"
    char_type = CharacterType.B
