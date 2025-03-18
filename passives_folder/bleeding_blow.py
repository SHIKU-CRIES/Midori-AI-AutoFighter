
class PassiveType:

    def __init__(self, name: str):
        self.name = name
        self.power: float = 1

    def activate(self, gamestate) -> None:
        """Applies the passive effect."""
        return gamestate

    def deal_damage(self, target):
        pass