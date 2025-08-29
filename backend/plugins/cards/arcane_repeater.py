import asyncio
from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class ArcaneRepeater(CardBase):
    """+240% ATK; 30% chance for attacks to repeat at 50% power."""

    id: str = "arcane_repeater"
    name: str = "Arcane Repeater"
    stars: int = 4
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 2.4})
    about: str = (
        "+240% ATK; each attack has a 30% chance to immediately repeat at 50% power."
    )

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _attack(attacker, target, amount) -> None:
            if attacker not in party.members:
                return
            if random.random() >= 0.30:
                return
            dmg = int(amount * 0.5)
            BUS.emit(
                "card_effect",
                self.id,
                attacker,
                "repeat_attack",
                dmg,
                {
                    "target": getattr(target, "id", str(target)),
                    "damage": dmg,
                    "original": amount,
                },
            )
            asyncio.create_task(target.apply_damage(dmg, attacker=attacker))

        BUS.subscribe("attack_used", _attack)
