from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class BulwarkTotem(CardBase):
    id: str = "bulwark_totem"
    name: str = "Bulwark Totem"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.02, "max_hp": 0.02})
    about: str = "+2% DEF & +2% HP; When an ally would die, redirect a small percentage of the fatal damage to this unit (tiny soak)"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_damage_taken(target, attacker, damage):
            # Check if target is one of our party members and damage is potentially fatal
            if target in party.members:
                current_hp = getattr(target, 'hp', 0)
                # If target is very low on HP (below 20%), try to soak some damage
                if current_hp <= getattr(target, 'max_hp', 1000) * 0.20:
                    # Find the card holder (member with this card equipped)
                    card_holder = None
                    for member in party.members:
                        if member != target and getattr(member, 'hp', 0) > 10:  # Must have reasonable HP
                            card_holder = member
                            break

                    if card_holder:
                        # Redirect 5% of damage to the card holder (tiny soak)
                        redirect_amount = max(1, int(damage * 0.05))
                        # Give some HP back to target, take it from card holder
                        hp_to_restore = min(redirect_amount, target.hp)
                        if hp_to_restore > 0:
                            target.hp += hp_to_restore
                            card_holder.hp = max(1, card_holder.hp - redirect_amount)

                            import logging
                            log = logging.getLogger(__name__)
                            log.debug("Bulwark Totem damage soak: %d damage soaked by %s for %s", redirect_amount, card_holder.id, target.id)
                            BUS.emit("card_effect", self.id, target, "damage_soak", redirect_amount, {
                                "soak_amount": redirect_amount,
                                "soaker": getattr(card_holder, 'id', 'unknown'),
                                "protected": getattr(target, 'id', 'unknown'),
                                "trigger_event": "damage_soak"
                            })

        BUS.subscribe("damage_taken", _on_damage_taken)
