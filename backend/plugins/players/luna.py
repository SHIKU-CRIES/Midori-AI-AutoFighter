from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types import load_damage_type
from plugins.damage_types._base import DamageTypeBase
from plugins.players._base import PlayerBase


@dataclass
class Luna(PlayerBase):
    id = "luna"
    name = "Luna"
    about = "A mystical lunar mage who draws power from the moon's phases. Her lunar reservoir stores celestial energy for powerful magical attacks."
    ##
    char_type: CharacterType = CharacterType.B
    damage_type: DamageTypeBase = field(
        default_factory=lambda: load_damage_type("Generic")
    )
    passives: list[str] = field(default_factory=lambda: ["luna_lunar_reservoir"])
    # UI hint: show numeric actions indicator
    actions_display: str = "number"
