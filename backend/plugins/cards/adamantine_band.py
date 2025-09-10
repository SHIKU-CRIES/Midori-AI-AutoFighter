from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class AdamantineBand(CardBase):
    id: str = "adamantine_band"
    name: str = "Adamantine Band"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"max_hp": 0.04})
    about: str = "+4% HP; If lethal damage would reduce you below 1 HP, reduce that damage by 10%"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_damage_taken(target, attacker, damage):
            # Check if target is one of our party members
            if target in party.members:
                current_hp = getattr(target, 'hp', 0)
                # Check if this damage would be lethal (reduce to 0 HP or below)
                if current_hp <= damage and current_hp > 0:
                    # Reduce damage by 10% - we'll modify target's HP to simulate the reduction
                    damage_reduction = int(damage * 0.10)
                    # Add back the damage reduction to HP to simulate reduced damage
                    if damage_reduction > 0:
                        target.hp = min(target.hp + damage_reduction, getattr(target, 'max_hp', 1000))
                        import logging
                        log = logging.getLogger(__name__)
                        log.debug("Adamantine Band lethal protection: +%d HP restored to %s", damage_reduction, target.id)
                        BUS.emit("card_effect", self.id, target, "lethal_protection", damage_reduction, {
                            "damage_reduction": damage_reduction,
                            "original_damage": damage,
                            "trigger_event": "lethal_damage"
                        })

        BUS.subscribe("damage_taken", _on_damage_taken)
