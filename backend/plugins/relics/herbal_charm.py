import asyncio
from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class HerbalCharm(RelicBase):
    """Heals all allies for 0.5% Max HP at the start of each turn."""

    id: str = "herbal_charm"
    name: str = "Herbal Charm"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "Heals all allies for 0.5% Max HP at the start of each turn per stack."

    def apply(self, party) -> None:
        def _heal(*_) -> None:
            for member in party.members:
                heal = int(member.max_hp * 0.005)
                asyncio.create_task(member.apply_healing(heal))

        BUS.subscribe("turn_start", _heal)

    def describe(self, stacks: int) -> str:
        pct = 0.5 * stacks
        return f"Heals all allies for {pct}% Max HP at the start of each turn."
