from autofighter.effects import DamageOverTime
from plugins.damage_types.lightning import Lightning
from plugins.damage_types._base import DamageTypeBase


class ChargedDecay(DamageOverTime):
    plugin_type = "dot"
    id = "charged_decay"
    damage_type: DamageTypeBase = Lightning()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Charged Decay", damage, turns, self.id)

    def tick(self, target, *_):
        alive = super().tick(target)
        if not alive:
            target.stunned = True
        return alive
