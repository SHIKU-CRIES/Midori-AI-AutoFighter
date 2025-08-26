import asyncio

from dataclasses import field
from dataclasses import dataclass

from autofighter.stats import BUS
from plugins.relics._base import RelicBase


@dataclass
class ArcaneFlask(RelicBase):
    """After an Ultimate, grant a shield equal to 20% Max HP per stack."""

    id: str = "arcane_flask"
    name: str = "Arcane Flask"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=dict)
    about: str = "After an Ultimate, grant a shield equal to 20% Max HP." 

    def apply(self, party) -> None:
        super().apply(party)

        def _ultimate(user) -> None:
            shield = int(user.max_hp * 0.2)
            asyncio.create_task(user.apply_healing(shield))

        BUS.subscribe("ultimate_used", _ultimate)

    def describe(self, stacks: int) -> str:
        pct = 20 * stacks
        return f"After an Ultimate, grant a shield equal to {pct}% Max HP."
