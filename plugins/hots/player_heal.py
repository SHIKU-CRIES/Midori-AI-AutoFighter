from autofighter.effects import HealingOverTime


class PlayerHeal(HealingOverTime):
    plugin_type = "hot"
    id = "player_heal"

    def __init__(self, player_name: str, healing: int, turns: int) -> None:
        super().__init__(f"{player_name}'s Heal", healing, turns, self.id)
