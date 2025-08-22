from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types.lightning import Lightning
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase

@dataclass
class LadyEcho(PlayerBase):
    id = "lady_echo"
    name = "LadyEcho"
    char_type = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(default_factory=Lightning)

