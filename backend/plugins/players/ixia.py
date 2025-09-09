from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Ixia(PlayerBase):
    id = "ixia"
    name = "Ixia"
    about = "A tiny but mighty lightning-wielder whose size belies her incredible power. Her tiny titan abilities generate massive electrical storms."
    char_type: CharacterType = CharacterType.A
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type("Lightning")
    )
    passives: list[str] = field(default_factory=lambda: ["ixia_tiny_titan"])
