from autofighter.effects import DamageOverTime
from plugins.damage_types.dark import Dark
from plugins.damage_types._base import DamageTypeBase


class ShadowSiphon(DamageOverTime):
    plugin_type = "dot"
    id = "shadow_siphon"
    damage_type: DamageTypeBase = Dark()

    def __init__(self, damage: int) -> None:
        super().__init__("Shadow Siphon", damage, 1, self.id)

    async def tick(self, target, *_):
        await super().tick(target)
        self.turns += 1
        return True
