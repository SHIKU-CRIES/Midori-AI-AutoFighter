from dataclasses import dataclass

from game.actors import CharacterType
from plugins.players._base import PlayerBase


@dataclass
class SamplePlayer(PlayerBase):
    id = "sample_player"
    name = "Sample Player"
    char_type = CharacterType.C
