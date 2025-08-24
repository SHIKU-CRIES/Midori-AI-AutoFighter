from autofighter.effects import DamageOverTime
from plugins.damage_types.ice import Ice
from plugins.damage_types._base import DamageTypeBase


class ColdWound(DamageOverTime):
    plugin_type = "dot"
    id = "cold_wound"
    damage_type: DamageTypeBase = Ice()
    max_stacks = 5

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Cold Wound", damage, turns, self.id)
