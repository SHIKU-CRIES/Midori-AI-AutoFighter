from autofighter.effects import DamageOverTime


class GaleErosion(DamageOverTime):
    plugin_type = "dot"
    id = "gale_erosion"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Gale Erosion", damage, turns, self.id)
