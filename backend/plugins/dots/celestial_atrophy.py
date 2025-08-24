from autofighter.effects import DamageOverTime
from plugins.damage_types.light import Light
from plugins.damage_types._base import DamageTypeBase


class CelestialAtrophy(DamageOverTime):
    plugin_type = "dot"
    id = "celestial_atrophy"
    damage_type: DamageTypeBase = Light()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Celestial Atrophy", damage, turns, self.id)

    def tick(self, target, *_):
        target.atk = max(target.atk - 1, 0)
        return super().tick(target)
