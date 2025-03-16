import typing

from typing import Tuple

class WeaponType:
    """Represents a weapon type with its attributes and passive effect."""

    def __init__(self, name: str, damage: int, accuracy: float, critical_chance: float, game_str: str) -> None:
        """Initializes a WeaponType object.

        Args:
            name: The name of the weapon.
            damage: The base damage of the weapon.
            accuracy: The accuracy of the weapon (0.0 to 1.0).
            critical_chance: The critical hit chance (0.0 to 1.0).
            passive: A callable or an object with an 'activate' method representing the passive effect.
            game_str: A string representation of the weapon in the game.
        """
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.critical_chance = critical_chance
        self.game_obj = game_str
        self.position: Tuple[int, int] = (0, 0)  # type: ignore