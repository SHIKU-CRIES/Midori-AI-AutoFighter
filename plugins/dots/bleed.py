from autofighter.effects import DamageOverTime


class Bleed(DamageOverTime):
    plugin_type = "dot"
    id = "bleed"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Bleed", damage, turns, self.id)
