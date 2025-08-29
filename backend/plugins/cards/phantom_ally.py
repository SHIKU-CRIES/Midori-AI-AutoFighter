import copy
from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class PhantomAlly(CardBase):
    id: str = "phantom_ally"
    name: str = "Phantom Ally"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 15.0})
    about: str = (
        "+1500% ATK; on the first turn, summon a temporary copy of a random ally."
    )

    async def apply(self, party):
        await super().apply(party)
        if not party.members:
            return
        original = random.choice(party.members)
        summon = copy.deepcopy(original)
        summon.id = f"{original.id}_phantom"
        party.members.append(summon)

        def _cleanup(_entity):
            if summon in party.members:
                party.members.remove(summon)
            BUS.unsubscribe("battle_end", _cleanup)

        BUS.subscribe("battle_end", _cleanup)
