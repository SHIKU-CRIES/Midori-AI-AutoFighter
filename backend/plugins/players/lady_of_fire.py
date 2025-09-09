from dataclasses import dataclass
from dataclasses import field

from autofighter.character import CharacterType
from plugins.damage_types._base import DamageTypeBase
from plugins.damage_types.fire import Fire
from plugins.players._base import PlayerBase


@dataclass
class LadyOfFire(PlayerBase):
    id = "lady_of_fire"
    name = "LadyOfFire"
    about = "A fierce pyromancer whose infernal momentum builds devastating heat waves. Her fire magic grows stronger with each enemy defeated."
    char_type: CharacterType = CharacterType.B
    damage_type: DamageTypeBase = field(default_factory=Fire)
    passives: list[str] = field(default_factory=lambda: ["lady_of_fire_infernal_momentum"])
