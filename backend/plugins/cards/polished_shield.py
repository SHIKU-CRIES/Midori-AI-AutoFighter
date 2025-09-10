from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class PolishedShield(CardBase):
    id: str = "polished_shield"
    name: str = "Polished Shield"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"defense": 0.03})
    about: str = "+3% DEF; When an ally resists a DoT/debuff, grant them +3 DEF for 1 turn"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        def _on_effect_resisted(target, effect_name, source):
            # Check if target is one of our party members and effect is DoT/debuff
            if target in party.members:
                effect_lower = effect_name.lower()
                is_dot_or_debuff = any(keyword in effect_lower for keyword in
                                     ['bleed', 'poison', 'burn', 'freeze', 'stun', 'silence', 'slow', 'weakness'])

                if is_dot_or_debuff:
                    # Grant +3 DEF for 1 turn
                    effect_manager = getattr(target, 'effect_manager', None)
                    if effect_manager is None:
                        effect_manager = EffectManager(target)
                        target.effect_manager = effect_manager

                    # Create temporary DEF buff
                    def_mod = create_stat_buff(
                        target,
                        name=f"{self.id}_resist_def",
                        turns=1,
                        defense_add=3  # +3 flat DEF
                    )
                    effect_manager.add_modifier(def_mod)

                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Polished Shield resist bonus: +3 DEF for 1 turn to %s", target.id)
                    BUS.emit("card_effect", self.id, target, "resist_def_bonus", 3, {
                        "def_bonus": 3,
                        "duration": 1,
                        "trigger_event": "effect_resisted",
                        "resisted_effect": effect_name
                    })

        BUS.subscribe("effect_resisted", _on_effect_resisted)
