from dataclasses import dataclass
from dataclasses import field
from itertools import count

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class IronGuard(CardBase):
    id: str = "iron_guard"
    name: str = "Iron Guard"
    stars: int = 2
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.55})
    about: str = "+55% DEF; damage grants all allies +10% DEF for 1 turn."

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)
        seq = count()

        def _damage_taken(victim, *_args) -> None:
            if victim not in party.members:
                return
            for member in party.members:
                mgr = getattr(member, "effect_manager", None)
                if mgr is None:
                    mgr = EffectManager(member)
                    member.effect_manager = mgr
                mod = create_stat_buff(
                    member,
                    name=f"{self.id}_{next(seq)}",
                    turns=1,
                    defense_mult=1.10,
                )
                mgr.add_modifier(mod)
                BUS.emit(
                    "card_effect",
                    self.id,
                    member,
                    "temporary_defense",
                    10,
                    {"source": getattr(victim, "id", "victim")},
                )

        BUS.subscribe("damage_taken", _damage_taken)
