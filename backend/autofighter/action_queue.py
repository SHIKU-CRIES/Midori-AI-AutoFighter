"""Simple action queue based on Speed (SPD) stats."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from .stats import GAUGE_START
from .stats import Stats


@dataclass
class ActionQueue:
    """Maintain turn order using an Action Gauge system.

    Each combatant starts with an action gauge of ``GAUGE_START``.  A combatant's
    base action value (AV) is ``GAUGE_START / SPD``.  During each step the actor
    with the lowest current AV takes a turn.  The amount of AV spent is deducted
    from every other combatant's AV, and the actor's AV is reset to its base
    value.
    """

    combatants: list[Stats] = field(default_factory=list)
    bonus_actors: list[Stats] = field(default_factory=list)

    def __post_init__(self) -> None:
        for c in self.combatants:
            c.action_gauge = GAUGE_START
            base = GAUGE_START / max(c.spd, 1)
            c.base_action_value = base
            c.action_value = base

    def grant_extra_turn(self, actor: Stats) -> None:
        """Queue ``actor`` for an immediate bonus turn."""
        if actor not in self.bonus_actors:
            self.bonus_actors.append(actor)

    def next_actor(self) -> Stats:
        """Return the combatant with the lowest action value and advance time."""
        if self.bonus_actors:
            return self.bonus_actors.pop(0)

        actor_index = min(
            range(len(self.combatants)),
            key=lambda i: self.combatants[i].action_value,
        )
        actor = self.combatants[actor_index]
        spent = actor.action_value
        for c in self.combatants:
            c.action_value -= spent
        actor.action_value = actor.base_action_value
        self.combatants.append(self.combatants.pop(actor_index))
        return actor

    def snapshot(self) -> list[dict[str, float]]:
        """Return queue state for serialization."""
        ordered = sorted(self.combatants, key=lambda c: c.action_value)
        extras = [
            {
                "id": getattr(c, "id", ""),
                "action_gauge": c.action_gauge,
                "action_value": c.action_value,
                "base_action_value": c.base_action_value,
                "bonus": True,
            }
            for c in self.bonus_actors
        ]
        return extras + [
            {
                "id": getattr(c, "id", ""),
                "action_gauge": c.action_gauge,
                "action_value": c.action_value,
                "base_action_value": c.base_action_value,
            }
            for c in ordered
        ]
