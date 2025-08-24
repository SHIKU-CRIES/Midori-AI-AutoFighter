import random

from autofighter.effects import DamageOverTime
from plugins.damage_types.ice import Ice
from plugins.damage_types._base import DamageTypeBase


class FrozenWound(DamageOverTime):
    plugin_type = "dot"
    id = "frozen_wound"
    damage_type: DamageTypeBase = Ice()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Frozen Wound", damage, turns, self.id)

    def tick(self, target, *_):
        if target.actions_per_turn > 1:
            target.actions_per_turn -= 1
        return super().tick(target)

    def on_action(self, target):
        stacks = target.dots.count(self.id)
        chance = min(0.01 * stacks, 1.0)
        if random.random() < chance:
            return False
        return None
