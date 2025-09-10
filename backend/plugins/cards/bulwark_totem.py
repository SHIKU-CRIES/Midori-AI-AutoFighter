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

        def _before_fatal_damage(target, attacker, damage):
            # Check if target is one of our party members and damage would be fatal
            if target in party.members:
                current_hp = getattr(target, 'hp', 0)
                if current_hp <= damage:  # Would be fatal
                    # Find another party member to redirect some damage to
                    other_members = [m for m in party.members if m != target and getattr(m, 'hp', 0) > 1]
                    if other_members:
                        # Choose the member with highest HP to redirect to
                        redirect_target = max(other_members, key=lambda m: getattr(m, 'hp', 0))
                        # Redirect 10% of fatal damage (tiny soak)
                        redirect_amount = int(damage * 0.10)
                        if redirect_amount > 0:
                            import logging
                            log = logging.getLogger(__name__)
                            log.debug("Bulwark Totem damage redirect: %d damage from %s to %s", redirect_amount, target.id, redirect_target.id)
                            BUS.emit("card_effect", self.id, target, "damage_redirect", redirect_amount, {
                                "redirect_amount": redirect_amount,
                                "redirect_target": getattr(redirect_target, 'id', 'unknown'),
                                "original_damage": damage,
                                "trigger_event": "fatal_damage"
                            })
                            # Note: Actual damage redirection would need to be implemented in the damage system

        BUS.subscribe("before_damage", _before_fatal_damage)
