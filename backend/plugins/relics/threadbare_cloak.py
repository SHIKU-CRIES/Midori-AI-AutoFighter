import asyncio

from dataclasses import field
from dataclasses import dataclass

from plugins.relics._base import RelicBase


@dataclass
class ThreadbareCloak(RelicBase):
    """Start battle with a small shield equal to 3% Max HP per stack."""

    id: str = "threadbare_cloak"
    name: str = "Threadbare Cloak"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {})
    about: str = "Start battle with a small shield equal to 3% Max HP per stack."

    def apply(self, party) -> None:
        super().apply(party)

        for member in party.members:
            shield = int(member.max_hp * 0.03)
            asyncio.create_task(member.apply_healing(shield))

    def describe(self, stacks: int) -> str:
        pct = 3 * stacks
        return f"Allies start battle with a shield equal to {pct}% Max HP."
