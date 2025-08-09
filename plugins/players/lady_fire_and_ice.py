from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class LadyFireAndIce(PlayerBase):
    id = "lady_fire_and_ice"
    name = "LadyFireAndIce"
    char_type = CharacterType.B
