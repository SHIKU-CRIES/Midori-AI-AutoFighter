from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Kboshi(PlayerBase):
    id = "kboshi"
    name = "Kboshi"
    about = "A master of dark energy whose flux cycle abilities harness the power of shadow and void. His energy manipulation creates devastating cyclical attacks."
    char_type: CharacterType = CharacterType.A
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type("Dark")
    )
    passives: list[str] = field(default_factory=lambda: ["kboshi_flux_cycle"])
