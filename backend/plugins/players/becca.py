from dataclasses import dataclass
from dataclasses import field
from random import choice

from autofighter.character import CharacterType
from plugins.damage_types import ALL_DAMAGE_TYPES
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Becca(PlayerBase):
    id = "becca"
    name = "Becca"
    about = "A sim human model excelling at administrative work with methodical precision. In her past life as an SDXL art generation bot, she learned to create beauty from code—skills that now help her organize chaos into victory."
    char_type: CharacterType = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type(choice(ALL_DAMAGE_TYPES))
    )
    passives: list[str] = field(default_factory=lambda: ["becca_menagerie_bond"])
