from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class MicroBlade(CardBase):
    id: str = "micro_blade"
    name: str = "Micro Blade"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 0.03})
    about: str = "+3% ATK; Attacks have a 6% chance to deal +8% bonus physical damage on hit"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_damage_dealt(attacker, target, damage, damage_type, source, source_action, action_name):
            # Check if attacker is one of our party members and this is an attack
            if attacker in party.members and action_name == "attack":
                # 6% chance to deal +8% bonus physical damage
                if random.random() < 0.06:
                    bonus_damage = int(damage * 0.08)
                    if bonus_damage > 0:
                        # Apply bonus damage immediately (physical damage type)
                        import asyncio
                        import logging
                        log = logging.getLogger(__name__)
                        try:
                            # Schedule the bonus damage asynchronously
                            asyncio.create_task(target.apply_damage(bonus_damage, attacker, source_type="physical", action_name="micro_blade_bonus"))
                            log.debug("Micro Blade bonus damage: +%d physical damage", bonus_damage)
                            BUS.emit("card_effect", self.id, attacker, "bonus_damage", bonus_damage, {
                                "bonus_damage": bonus_damage,
                                "trigger_chance": 0.06,
                                "damage_type": "physical"
                            })
                        except Exception as e:
                            log.warning("Error applying Micro Blade bonus damage: %s", e)

        BUS.subscribe("damage_dealt", _on_damage_dealt)
