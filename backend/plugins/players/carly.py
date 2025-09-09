from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.light import Light
from plugins.players._base import PlayerBase


@dataclass
class Carly(PlayerBase):
    id = "carly"
    name = "Carly"
    about = "A sim human model dedicated to protecting others above all else. Her protective instincts run deep in her programming, making her an unwavering guardian who always puts people's safety first."
    char_type: CharacterType = CharacterType.B
    gacha_rarity = 5
    damage_type: DamageTypeBase = field(default_factory=Light)
    stat_gain_map: dict[str, str] = field(
        default_factory=lambda: {"atk": "defense"}
    )
    passives: list[str] = field(default_factory=lambda: ["carly_guardians_aegis"])
    # UI hint: show numeric actions indicator
    actions_display: str = "number"
