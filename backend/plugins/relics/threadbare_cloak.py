from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase


@dataclass
class ThreadbareCloak(RelicBase):
    """Start battle with a small shield equal to 3% Max HP per stack."""

    id: str = "threadbare_cloak"
    name: str = "Threadbare Cloak"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {})

    def apply(self, party) -> None:
        super().apply(party)

        for member in party.members:
            member.hp += int(member.max_hp * 0.03)
