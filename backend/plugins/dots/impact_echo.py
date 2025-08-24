from autofighter.effects import DamageOverTime
from plugins.damage_types.generic import Generic
from plugins.damage_types._base import DamageTypeBase


class ImpactEcho(DamageOverTime):
    plugin_type = "dot"
    id = "impact_echo"
    damage_type: DamageTypeBase = Generic()

    def __init__(self, turns: int = 3) -> None:
        super().__init__("Impact Echo", 0, turns, self.id)

    def tick(self, target, *_):
        self.damage = int(target.last_damage_taken * 0.5)
        return super().tick(target)
