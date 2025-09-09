from dataclasses import dataclass
from dataclasses import field
from random import choice

from autofighter.character import CharacterType
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class LadyFireAndIce(PlayerBase):
    id = "lady_fire_and_ice"
    name = "LadyFireAndIce"
    char_type: CharacterType = CharacterType.B
    gacha_rarity = 6
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type(choice(["Fire", "Ice"]))
    )
    passives: list[str] = field(default_factory=lambda: ["lady_fire_and_ice_duality_engine"])
