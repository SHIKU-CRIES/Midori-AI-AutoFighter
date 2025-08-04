from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Stats:
    """Basic combat statistics shared by players and foes."""

    hp: int
    max_hp: int
    atk: int = 0
    defense: int = 0

    def apply_damage(self, amount: int) -> None:
        """Reduce HP by ``amount`` without going below zero."""
        self.hp = max(self.hp - amount, 0)

    def apply_healing(self, amount: int) -> None:
        """Increase HP by ``amount`` without exceeding ``max_hp``."""
        self.hp = min(self.hp + amount, self.max_hp)
