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
    about = "A diminutive but fierce lightning-wielder whose compact frame channels tremendous electrical energy. Despite her small stature, Ixia's lightning abilities make her a formidable Type A combatant."
    char_type: CharacterType = CharacterType.A
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type("Lightning")
    )
    passives: list[str] = field(default_factory=lambda: ["ixia_tiny_titan"])
