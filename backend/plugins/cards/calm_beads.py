from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class CalmBeads(CardBase):
    id: str = "calm_beads"
    name: str = "Calm Beads"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"effect_resistance": 0.03})
    about: str = "+3% Effect Res; On resisting a debuff, gain +1 small energy for next action"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_effect_resisted(target, effect_name, source):
            # Check if target is one of our party members and effect is a debuff
            if target in party.members:
                effect_lower = effect_name.lower()
                is_debuff = any(keyword in effect_lower for keyword in
                               ['bleed', 'poison', 'burn', 'freeze', 'stun', 'silence', 'slow', 'weakness', 'curse'])

                if is_debuff:
                    # Grant +1 energy
                    old_energy = getattr(target, 'energy', 0)
                    max_energy = getattr(target, 'max_energy', 100)
                    if hasattr(target, 'energy'):
                        target.energy = min(max_energy, old_energy + 1)
                        import logging
                        log = logging.getLogger(__name__)
                        log.debug("Calm Beads energy refund: +1 energy to %s", target.id)
                        BUS.emit("card_effect", self.id, target, "resist_energy_gain", 1, {
                            "energy_gained": 1,
                            "resisted_effect": effect_name,
                            "trigger_event": "effect_resisted"
                        })

        BUS.subscribe("effect_resisted", _on_effect_resisted)
