from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from autofighter.stats import Stats
from plugins.cards._base import CardBase
from plugins.cards._base import safe_async_task


@dataclass
class Overclock(CardBase):
    """+240% ATK & Effect Hit Rate; allies act twice at battle start."""

    id: str = "overclock"
    name: str = "Overclock"
    stars: int = 4
    effects: dict[str, float] = field(
        default_factory=lambda: {"atk": 2.4, "effect_hit_rate": 2.4}
    )
    about: str = (
        "+240% ATK & +240% Effect Hit Rate; at the start of each battle, "
        "all allies immediately take two actions back to back."
    )

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        foes: list[Stats] = []

        async def _double_act(ally: Stats) -> None:
            for _ in range(2):
                alive = [f for f in foes if f.hp > 0]
                if ally.hp <= 0 or not alive:
                    break
                target = random.choice(alive)
                dmg = await target.apply_damage(ally.atk, attacker=ally)
                BUS.emit("attack_used", ally, target, dmg)
                BUS.emit(
                    "card_effect",
                    self.id,
                    ally,
                    "extra_action",
                    dmg,
                    {"target": getattr(target, "id", str(target)), "damage": dmg},
                )

        def _battle_start(entity: Stats) -> None:
            if entity in party.members:
                safe_async_task(_double_act(entity))
            else:
                foes.append(entity)

        BUS.subscribe("battle_start", _battle_start)
