from dataclasses import dataclass
from dataclasses import field
from random import choice

from autofighter.character import CharacterType
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Hilander(PlayerBase):
    id = "hilander"
    name = "Hilander"
    about = "A passionate brewmaster whose critical ferment techniques create explosive combinations. His alchemical prowess turns the tide of battle through strategic enhancement."
    char_type: CharacterType = CharacterType.A
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type(choice(ALL_DAMAGE_TYPES))
    )
    passives: list[str] = field(default_factory=lambda: ["hilander_critical_ferment"])
