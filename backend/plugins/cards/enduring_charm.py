from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import EffectManager
from autofighter.effects import create_stat_buff
from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class EnduringCharm(CardBase):
    id: str = "enduring_charm"
    name: str = "Enduring Charm"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"vitality": 0.03})
    about: str = "+3% Vitality; When below 30% HP, gain +3% Vitality for 2 turns"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        # Track which members have the vitality boost active to avoid stacking
        active_boosts = set()

        def _check_low_hp():
            for member in party.members:
                member_id = id(member)
                current_hp = getattr(member, 'hp', 0)
                max_hp = getattr(member, 'max_hp', 1)

                # Check if below 30% HP and not already has boost
                if current_hp / max_hp < 0.30 and member_id not in active_boosts:
                    # Add to active set
                    active_boosts.add(member_id)

                    # Apply +3% vitality for 2 turns
                    effect_manager = getattr(member, 'effect_manager', None)
                    if effect_manager is None:
                        effect_manager = EffectManager(member)
                        member.effect_manager = effect_manager

                    # Create vitality buff
                    vit_mod = create_stat_buff(
                        member,
                        name=f"{self.id}_low_hp_vit",
                        turns=2,
                        vitality_mult=1.03  # +3% vitality
                    )
                    effect_manager.add_modifier(vit_mod)

                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Enduring Charm activated vitality boost for %s: +3% vitality for 2 turns", member.id)
                    BUS.emit("card_effect", self.id, member, "vitality_boost", 3, {
                        "vitality_boost": 3,
                        "duration": 2,
                        "trigger_threshold": 0.30
                    })

                    # Remove from active set after some time (simplified)
                    def _remove_boost():
                        if member_id in active_boosts:
                            active_boosts.remove(member_id)

                    # Schedule removal (in real implementation, this would be handled by effect expiration)
                    import asyncio
                    asyncio.get_event_loop().call_later(20, _remove_boost)  # Remove after 20 seconds

        # Check HP at the start of each turn and after damage taken
        BUS.subscribe("turn_start", _check_low_hp)

        def _on_damage_taken(target, attacker, damage):
            _check_low_hp()

        BUS.subscribe("damage_taken", _on_damage_taken)

        def _cleanup(*_: object) -> None:
            BUS.unsubscribe("turn_start", _check_low_hp)
            BUS.unsubscribe("damage_taken", _on_damage_taken)
            BUS.unsubscribe("battle_end", _cleanup)

        BUS.subscribe("battle_end", _cleanup)
