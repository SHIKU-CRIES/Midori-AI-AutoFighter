from autofighter.effects import DamageOverTime


class TwilightDecay(DamageOverTime):
    plugin_type = "dot"
    id = "twilight_decay"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Twilight Decay", damage, turns, self.id)
