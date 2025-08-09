from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class Bubbles(PlayerBase):
    id = "bubbles"
    name = "Bubbles"
    char_type = CharacterType.A
