from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types import get_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Mimic(PlayerBase):
    id = "mimic"
    name = "Mimic"
    char_type: CharacterType = CharacterType.C
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: get_damage_type("Mimic")
    )
    passives: list[str] = field(default_factory=lambda: ["mimic_player_copy"])
