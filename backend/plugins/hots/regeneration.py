from autofighter.effects import HealingOverTime
from plugins.damage_types.generic import Generic
from plugins.damage_types._base import DamageTypeBase


class Regeneration(HealingOverTime):
    plugin_type = "hot"
    id = "regeneration"
    damage_type: DamageTypeBase = Generic()

    def __init__(self, healing: int, turns: int) -> None:
        super().__init__("Regeneration", healing, turns, self.id)
