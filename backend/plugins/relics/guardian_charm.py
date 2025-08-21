from dataclasses import dataclass
from dataclasses import field

from plugins.relics._base import RelicBase
from autofighter.stats import BUS


@dataclass
class GuardianCharm(RelicBase):
    """At battle start, grants +20% DEF to the lowest-HP ally."""

    id: str = "guardian_charm"
    name: str = "Guardian Charm"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=dict)

    def apply(self, party) -> None:
        if not party.members:
            return
        member = min(party.members, key=lambda m: m.hp)
        member.defense = int(member.defense * 1.2)
