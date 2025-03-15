from typing import Optional, Dict, Any

class dot:
    """
    Represents a Damage Over Time (DOT) effect applied to a character or entity.

    Attributes:
        name (str): The name of the DOT effect (e.g., "Poison," "Burn").
        damage (float): The amount of damage dealt per turn by the DOT.
        turns (int): The number of turns the DOT effect lasts.  Must be greater than 0.
        damage_type (str):  The type of damage the DOT inflicts (e.g., "fire", "poison", "bleed").
        source (Optional[str]):  Optional name or identifier of the entity that applied the DOT.  Helps track responsibility.
        metadata (Optional[Dict[str, Any]]):  Optional dictionary for storing extra information, like the spell or ability that caused the DOT.
        tick_interval (int): how many times to do the effect each turn, good if you want to do it fast and for less time.

    Raises:
        ValueError: If 'turns' is not a positive integer.
    """
    def __init__(self, name: str, damage: float, turns: int, damage_type: str = "generic", source: Optional[str] = None, tick_interval: int = 1, metadata: Optional[Dict[str, Any]] = None) -> None:
        if not isinstance(turns, int) or turns <= 0:
            raise ValueError("Turns must be a positive integer.")

        self.name: str = name
        self.damage: float = damage
        self.turns: int = turns
        self.damage_type: str = damage_type
        self.source: Optional[str] = source
        self.metadata: Optional[Dict[str, Any]] = metadata
        self.tick_interval: int = tick_interval

    def __repr__(self) -> str:
        return f"DOT(name='{self.name}', damage={self.damage}, turns={self.turns}, type={self.damage_type})"

    def tick(self) -> int:
        """
        Reduces the remaining duration of the DOT.

        Returns:
            The damage dealt this tick.  Returns 0 if the DOT has expired.
        """
        if self.turns > 0:
            self.turns -= 1
            return self.damage
        return 0

    def is_active(self) -> bool:
        """
        Checks if the DOT is still active (has remaining turns).

        Returns:
            True if the DOT is active, False otherwise.
        """
        return self.turns > 0