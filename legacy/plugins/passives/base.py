from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for type hints only
    from player import Player


class PassiveType:
    """Base type for all passives."""

    def __init__(self, name: str):
        self.name = name
        self.power: float = 1

    def activate(self, gamestate) -> None:
        """Applies the passive effect."""
        return gamestate

    def do_pre_turn(self):
        """Hook before a turn begins."""

    def heal_damage(self, input_healing: float):
        """Modify incoming healing."""

    def take_damage(self, input_damage: float):
        """Modify incoming damage."""

    def deal_damage(self, input_damage_mod: float):
        """Modify outgoing damage."""

    def damage_mitigation(self, damage_pre: float):
        """Adjust damage mitigation effects."""

    def regain_hp(self):
        """Adjust HP regain effects."""

    def damage_over_time(self):
        """Tick damage-over-time effects."""

    def heal_over_time(self):
        """Tick healing-over-time effects."""

    def crit_damage_mod(self, damage_pre: float):
        """Modify critical damage scaling."""


class PassivePlugin(PassiveType, ABC):
    """Base class for passive plugins."""

    plugin_type: str
    id: str
    name: str

    @abstractmethod
    def on_apply(self, player: Player) -> None:
        """Grant the passive's effect to ``player``."""
        raise NotImplementedError
