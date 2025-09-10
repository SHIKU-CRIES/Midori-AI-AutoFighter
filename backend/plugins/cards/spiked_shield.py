from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class SpikedShield(CardBase):
    id: str = "spiked_shield"
    name: str = "Spiked Shield"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 0.03, "defense": 0.03})
    about: str = "+3% ATK & +3% DEF; When mitigation triggers (block threshold), deal small retaliatory damage (3% of attack)"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_mitigation_triggered(target, original_damage, mitigated_damage):
            # Check if target is one of our party members and mitigation actually reduced damage
            if target in party.members and mitigated_damage < original_damage:
                # Deal retaliatory damage (3% of attack)
                attacker_stat = getattr(target, 'atk', 0)
                if attacker_stat == 0:
                    attacker_stat = getattr(target, 'attack', 0)
                retaliation_damage = int(attacker_stat * 0.03)

                if retaliation_damage > 0:
                    # Find the original attacker (this would need to be passed in the event)
                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Spiked Shield retaliation: %d damage from %s", retaliation_damage, target.id)
                    BUS.emit("card_effect", self.id, target, "retaliation_damage", retaliation_damage, {
                        "retaliation_damage": retaliation_damage,
                        "damage_mitigated": original_damage - mitigated_damage,
                        "trigger_event": "mitigation"
                    })
                    # Note: Actual retaliation damage would need to be applied to the original attacker

        BUS.subscribe("mitigation_triggered", _on_mitigation_triggered)
