import asyncio
from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.party import Party
from autofighter.stats import BUS
from plugins.cards._base import CardBase
from plugins.foes._base import FoeBase


@dataclass
class ArcLightning(CardBase):
    id: str = "arc_lightning"
    name: str = "Arc Lightning"
    stars: int = 3
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 2.55})
    about: str = (
        "+255% ATK; every attack chains 50% of dealt damage to a random foe."
    )

    async def apply(self, party: Party) -> None:
        await super().apply(party)
        foes: list[FoeBase] = []

        def _battle_start(entity) -> None:
            if isinstance(entity, FoeBase):
                foes.append(entity)

        def _battle_end(entity) -> None:
            if isinstance(entity, FoeBase) and entity in foes:
                foes.remove(entity)
            if entity in party.members:
                BUS.unsubscribe("hit_landed", _hit)
                BUS.unsubscribe("battle_start", _battle_start)
                BUS.unsubscribe("battle_end", _battle_end)

        def _hit(attacker, target, amount, source, *_):
            if attacker not in party.members or source != "attack":
                return
            valid = [f for f in foes if f.hp > 0 and f is not target]
            if not valid:
                return
            extra = random.choice(valid)
            extra_dmg = int(amount * 0.5)
            asyncio.create_task(extra.apply_damage(extra_dmg, attacker, trigger_on_hit=False))
            BUS.emit(
                "card_effect",
                self.id,
                attacker,
                "chain",
                extra_dmg,
                {"target": getattr(extra, "id", str(extra))},
            )

        BUS.subscribe("battle_start", _battle_start)
        BUS.subscribe("battle_end", _battle_end)
        BUS.subscribe("hit_landed", _hit)
