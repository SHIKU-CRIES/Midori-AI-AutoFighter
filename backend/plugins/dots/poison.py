from autofighter.effects import DamageOverTime
from plugins.damage_types.generic import Generic
from plugins.damage_types._base import DamageTypeBase


class Poison(DamageOverTime):
    plugin_type = "dot"
    id = "poison"
    damage_type: DamageTypeBase = Generic()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Poison", damage, turns, self.id)
