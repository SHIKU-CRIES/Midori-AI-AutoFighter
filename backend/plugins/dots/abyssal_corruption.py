from autofighter.effects import DamageOverTime
from plugins.damage_types.dark import Dark
from plugins.damage_types._base import DamageTypeBase


class AbyssalCorruption(DamageOverTime):
    plugin_type = "dot"
    id = "abyssal_corruption"
    damage_type: DamageTypeBase = Dark()

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Abyssal Corruption", damage, turns, self.id)

    def on_death(self, target_manager) -> None:
        target_manager.add_dot(AbyssalCorruption(self.damage, self.turns))
