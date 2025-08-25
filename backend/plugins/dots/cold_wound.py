from autofighter.effects import DamageOverTime


class ColdWound(DamageOverTime):
    plugin_type = "dot"
    id = "cold_wound"
    max_stacks = 5

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Cold Wound", damage, turns, self.id)
