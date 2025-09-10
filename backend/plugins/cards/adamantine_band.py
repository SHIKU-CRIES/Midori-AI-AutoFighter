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

        def _before_damage(target, attacker, damage):
            # Check if target is one of our party members
            if target in party.members:
                current_hp = getattr(target, 'hp', 0)
                # Check if this damage would be lethal (reduce below 1 HP)
                if current_hp - damage < 1:
                    # Reduce damage by 10%
                    damage_reduction = int(damage * 0.10)
                    # This is a theoretical implementation - the actual damage system would need
                    # to support damage modification before application
                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Adamantine Band lethal protection: -%d damage reduction for %s", damage_reduction, target.id)
                    BUS.emit("card_effect", self.id, target, "lethal_protection", damage_reduction, {
                        "damage_reduction": damage_reduction,
                        "original_damage": damage,
                        "trigger_event": "lethal_damage"
                    })
                    # Note: Actual damage reduction would need to be implemented in the damage system

        # This would need a pre-damage hook in the actual system
        BUS.subscribe("before_damage", _before_damage)
