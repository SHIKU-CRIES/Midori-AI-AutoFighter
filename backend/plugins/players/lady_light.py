from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.light import Light
from plugins.players._base import PlayerBase


@dataclass
class LadyLight(PlayerBase):
    id = "lady_light"
    name = "LadyLight"
    char_type = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(default_factory=Light)
