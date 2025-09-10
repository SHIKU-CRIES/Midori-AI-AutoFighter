from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class MindfulTassel(CardBase):
    id: str = "mindful_tassel"
    name: str = "Mindful Tassel"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"effect_hit_rate": 0.03})
    about: str = "+3% Effect Hit Rate; First debuff applied each battle has +5% potency"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        first_debuff_used = {}

        def _on_effect_applied(target, effect_name, duration, source):
            # Check if source is one of our party members and this is a debuff
            if source in party.members:
                source_id = id(source)
                effect_lower = effect_name.lower()
                is_debuff = any(keyword in effect_lower for keyword in
                               ['bleed', 'poison', 'burn', 'freeze', 'stun', 'silence', 'slow', 'weakness', 'curse'])

                if is_debuff and source_id not in first_debuff_used:
                    # Mark first debuff as used for this member
                    first_debuff_used[source_id] = True

                    # Increase potency by 5% (theoretical implementation)
                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Mindful Tassel first debuff potency: +5% potency to %s", effect_name)
                    BUS.emit("card_effect", self.id, source, "debuff_potency_boost", 5, {
                        "potency_boost": 5,
                        "effect_name": effect_name,
                        "trigger_event": "first_debuff"
                    })

        def _on_battle_start(target):
            # Reset first debuff usage for new battle
            if target in party.members:
                first_debuff_used.clear()

        BUS.subscribe("effect_applied", _on_effect_applied)
        BUS.subscribe("battle_start", _on_battle_start)
