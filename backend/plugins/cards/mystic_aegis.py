import asyncio
from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class MysticAegis(CardBase):
    id: str = "mystic_aegis"
    name: str = "Mystic Aegis"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=lambda: {"effect_resistance": 0.55})
    about: str = "+55% Effect Res; resisting a debuff heals 5% Max HP."

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _resisted(member) -> None:
            if member not in party.members:
                return
            heal = int(member.max_hp * 0.05)
            BUS.emit(
                "card_effect",
                self.id,
                member,
                "healing",
                heal,
                {"heal_amount": heal},
            )
            asyncio.create_task(member.apply_healing(heal))

        BUS.subscribe("debuff_resisted", _resisted)
