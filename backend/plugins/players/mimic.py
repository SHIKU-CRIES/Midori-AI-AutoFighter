from dataclasses import dataclass
from dataclasses import field
from random import choice

from autofighter.character import CharacterType
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Mimic(PlayerBase):
    id = "mimic"
    name = "Mimic"
    about = "A mysterious shapeshifter who perfectly copies other fighters' abilities. Its player copy skill allows it to adapt to any combat situation."
    char_type: CharacterType = CharacterType.C
    gacha_rarity = 0
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type(choice(ALL_DAMAGE_TYPES))
    )
    passives: list[str] = field(default_factory=lambda: ["mimic_player_copy"])
