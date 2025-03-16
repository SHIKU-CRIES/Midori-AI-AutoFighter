
class PassiveType:
    """
    A class to represent a passive type with source and target type checks.
    """

    def __init__(self, name: str):
        """
        Initializes the PassiveType object.

        Args:
            name: The name of the passive.
        """
        self.name = name

    def activate(self, gamestate) -> None:
        """Applies the passive effect."""
        return gamestate