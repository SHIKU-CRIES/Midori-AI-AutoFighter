from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class LadyLight(PlayerBase):
    id = "lady_light"
    name = "LadyLight"
    char_type = CharacterType.B
