from __future__ import annotations

import logging

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Optional

if TYPE_CHECKING:
    from autofighter.stats import Stats
    from autofighter.effects import DamageOverTime


log = logging.getLogger(__name__)


@dataclass
class DamageTypeBase:
    """Base class for damage type plugins."""

    plugin_type = "damage_type"

    id: str = "Generic"
    weakness: str = "none"
    color: tuple[int, int, int] = (255, 255, 255)

    def is_weak(self, type_check: str) -> bool:
        return type_check == self.weakness

    def is_resistance(self, type_check: str) -> bool:
        return type_check == self.id or self.id == "Generic"

    def damage_mod(self, incoming_damage: float, incoming_type: str) -> float:
        log.debug(
            "%s modifying damage %s from %s",
            self.id,
            incoming_damage,
            incoming_type,
        )
        if self.is_weak(incoming_type):
            return incoming_damage * 1.25
        if self.is_resistance(incoming_type):
            return incoming_damage * 0.75
        return incoming_damage

    async def on_action(
        self, actor: "Stats", allies: list["Stats"], enemies: list["Stats"]
    ) -> bool:
        """Called before ``actor`` takes an action.

        Return ``False`` to cancel the action.
        """

        return True

    # Event hooks -----------------------------------------------------------

    def on_hit(self, attacker: Stats, target: Stats) -> None:
        """Called when ``attacker`` successfully hits ``target``."""
        log.debug("%s hit %s", attacker.id, target.id)

    def on_damage(self, damage: float, attacker: Stats, target: Stats) -> float:
        """Called before damage is applied; return the modified ``damage``."""

        log.debug("%s on_damage %s -> %s", attacker.id, target.id, damage)
        return damage

    def on_damage_taken(self, damage: float, attacker: Stats, target: Stats) -> float:
        """Called when ``target`` takes damage; return the modified ``damage``."""

        log.debug("%s on_damage_taken %s -> %s", attacker.id, target.id, damage)
        return damage

    def on_dot_damage_taken(
        self, damage: float, attacker: Stats, target: Stats
    ) -> float:
        """Called when ``target`` takes DoT damage; return the modified ``damage``."""

        log.debug("%s on_dot_damage_taken %s -> %s", attacker.id, target.id, damage)
        return damage

    def on_party_damage_taken(
        self, damage: float, attacker: Stats, target: Stats
    ) -> float:
        """Called when a party member takes damage; return the modified ``damage``."""

        log.debug("%s on_party_damage_taken %s -> %s", attacker.id, target.id, damage)
        return damage

    def on_party_dot_damage_taken(
        self, damage: float, attacker: Stats, target: Stats
    ) -> float:
        """Called when a party member takes DoT damage; return the modified ``damage``."""

        log.debug(
            "%s on_party_dot_damage_taken %s -> %s", attacker.id, target.id, damage
        )
        return damage

    def on_death(self, attacker: Stats, target: Stats) -> None:
        """Called when ``target`` dies."""
        log.info("%s killed %s", attacker.id, target.id)

    def on_party_member_death(self, attacker: Stats, target: Stats) -> None:
        """Called when a party member dies."""
        log.info("Party member %s died to %s", target.id, attacker.id)

    def on_heal(self, heal: float, healer: Stats, target: Stats) -> float:
        """Called before healing is applied; return the modified ``heal``."""

        log.debug("%s on_heal %s -> %s", healer.id, target.id, heal)
        return heal

    def on_heal_received(self, heal: float, healer: Stats, target: Stats) -> float:
        """Called when ``target`` is healed; return the modified ``heal``."""

        log.debug("%s on_heal_received %s -> %s", healer.id, target.id, heal)
        return heal

    def on_hot_heal_received(self, heal: float, healer: Stats, target: Stats) -> float:
        """Called when ``target`` receives HoT healing; return the modified ``heal``."""

        log.debug("%s on_hot_heal_received %s -> %s", healer.id, target.id, heal)
        return heal

    def on_party_heal_received(
        self, heal: float, healer: Stats, target: Stats
    ) -> float:
        """Called when a party member is healed; return the modified ``heal``."""

        log.debug("%s on_party_heal_received %s -> %s", healer.id, target.id, heal)
        return heal

    def on_party_hot_heal_received(
        self, heal: float, healer: Stats, target: Stats
    ) -> float:
        """Called when a party member receives HoT healing; return the modified ``heal``."""

        log.debug("%s on_party_hot_heal_received %s -> %s", healer.id, target.id, heal)
        return heal

    def create_dot(self, damage: float, source: Stats) -> Optional["DamageOverTime"]:
        """Return a DoT effect based on ``damage`` or ``None`` to skip."""

        log.debug("%s create_dot %s", self.id, damage)
        return None
