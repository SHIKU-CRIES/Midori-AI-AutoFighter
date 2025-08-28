from autofighter.effects import HealingOverTime


class Regeneration(HealingOverTime):
    plugin_type = "hot"
    id = "regeneration"

    def __init__(self, healing: int, turns: int) -> None:
        super().__init__("Regeneration", healing, turns, self.id)
