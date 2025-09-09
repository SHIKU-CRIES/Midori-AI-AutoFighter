from dataclasses import dataclass
from dataclasses import field
from random import choice

from autofighter.character import CharacterType
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Graygray(PlayerBase):
    id = "graygray"
    name = "Graygray"
    about = "A tactical mastermind whose counter maestro abilities turn enemy attacks into strategic advantages. Every strike against her becomes a lesson in combat."
    char_type: CharacterType = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type(choice(ALL_DAMAGE_TYPES))
    )
    passives: list[str] = field(default_factory=lambda: ["graygray_counter_maestro"])
