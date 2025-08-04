from autofighter.effects import DamageOverTime


class ImpactEcho(DamageOverTime):
    plugin_type = "dot"
    id = "impact_echo"

    def __init__(self, damage: int, turns: int) -> None:
        super().__init__("Impact Echo", damage, turns, self.id)
