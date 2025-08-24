from autofighter.effects import DamageOverTime
from plugins.damage_types.wind import Wind
from plugins.damage_types._base import DamageTypeBase


class GaleErosion(DamageOverTime):
    plugin_type = "dot"
    id = "gale_erosion"
    damage_type: DamageTypeBase = Wind()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Gale Erosion", damage, turns, self.id)

    def tick(self, target, *_):
        target.mitigation = max(target.mitigation - 1, 0)
        return super().tick(target)
