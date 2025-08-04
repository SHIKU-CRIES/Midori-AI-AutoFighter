from autofighter.effects import DamageOverTime


class AbyssalWeakness(DamageOverTime):
    plugin_type = "dot"
    id = "abyssal_weakness"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Abyssal Weakness", damage, turns, self.id)
