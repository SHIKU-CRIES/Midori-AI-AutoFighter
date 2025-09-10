from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class LuckyCoin(CardBase):
    id: str = "lucky_coin"
    name: str = "Lucky Coin"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"crit_rate": 0.03})
    about: str = "+3% Crit Rate; On critical hit, 20% chance to refund a tiny energy to the attacker"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_critical_hit(attacker, target, damage, action_name):
            # Check if attacker is one of our party members
            if attacker in party.members:
                # 20% chance to refund tiny energy
                if random.random() < 0.20:
                    # Refund 1 energy (tiny amount)
                    old_energy = getattr(attacker, 'energy', 0)
                    energy_refund = 1
                    if hasattr(attacker, 'energy'):
                        attacker.energy = min(getattr(attacker, 'max_energy', 100), old_energy + energy_refund)
                        import logging
                        log = logging.getLogger(__name__)
                        log.debug("Lucky Coin energy refund: +%d energy to %s", energy_refund, attacker.id)
                        BUS.emit("card_effect", self.id, attacker, "energy_refund", energy_refund, {
                            "energy_refund": energy_refund,
                            "trigger_chance": 0.20,
                            "trigger_event": "critical_hit"
                        })

        BUS.subscribe("critical_hit", _on_critical_hit)
