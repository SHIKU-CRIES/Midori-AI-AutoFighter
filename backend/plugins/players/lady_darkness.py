from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.dark import Dark
from plugins.players._base import PlayerBase


@dataclass
class LadyDarkness(PlayerBase):
    id = "lady_darkness"
    name = "LadyDarkness"
    char_type: CharacterType = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(default_factory=Dark)
    passives: list[str] = field(default_factory=lambda: ["lady_darkness_eclipsing_veil"])
