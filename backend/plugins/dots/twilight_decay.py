from autofighter.effects import DamageOverTime
from plugins.damage_types.generic import Generic
from plugins.damage_types._base import DamageTypeBase


class TwilightDecay(DamageOverTime):
    plugin_type = "dot"
    id = "twilight_decay"
    damage_type: DamageTypeBase = Generic()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Twilight Decay", damage, turns, self.id)

    def tick(self, target, *_):
        target.vitality -= 0.5
        return super().tick(target)
