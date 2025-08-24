from autofighter.effects import DamageOverTime
from plugins.damage_types.fire import Fire
from plugins.damage_types._base import DamageTypeBase


class BlazingTorment(DamageOverTime):
    plugin_type = "dot"
    id = "blazing_torment"
    damage_type: DamageTypeBase = Fire()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Blazing Torment", damage, turns, self.id)

    async def on_action(self, target) -> None:
        await super().tick(target)
