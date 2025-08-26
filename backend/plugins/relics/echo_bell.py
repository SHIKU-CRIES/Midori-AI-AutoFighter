import asyncio

from dataclasses import field
from dataclasses import dataclass

from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class EchoBell(RelicBase):
    """First action each battle repeats at 15% power per stack."""

    id: str = "echo_bell"
    name: str = "Echo Bell"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "First action each battle repeats at 15% power per stack."

    def apply(self, party) -> None:
        super().apply(party)

        used: set[int] = set()

        def _battle_start() -> None:
            used.clear()

        def _action(actor, target, amount) -> None:
            pid = id(actor)
            if pid in used:
                return
            used.add(pid)
            dmg = int(amount * 0.15)
            asyncio.create_task(target.apply_damage(dmg, attacker=actor))

        BUS.subscribe("battle_start", lambda: _battle_start())
        BUS.subscribe("action_used", _action)

    def describe(self, stacks: int) -> str:
        pct = 15 * stacks
        return f"First action each battle repeats at {pct}% power."
