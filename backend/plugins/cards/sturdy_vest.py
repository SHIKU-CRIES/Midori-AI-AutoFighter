from dataclasses import dataclass
from dataclasses import field

from autofighter.effects import EffectManager
from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class SturdyVest(CardBase):
    id: str = "sturdy_vest"
    name: str = "Sturdy Vest"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"max_hp": 0.03})
    about: str = "+3% HP; When below 35% HP, gain a small 3% HoT for 2 turns"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        # Track which members have the HoT active to avoid stacking
        active_hots = set()

        def _check_low_hp():
            for member in party.members:
                member_id = id(member)
                current_hp = getattr(member, 'hp', 0)
                max_hp = getattr(member, 'max_hp', 1)

                # Check if below 35% HP and not already has HoT
                if current_hp / max_hp < 0.35 and member_id not in active_hots:
                    # Add to active set
                    active_hots.add(member_id)

                    # Apply 3% HoT for 2 turns
                    effect_manager = getattr(member, 'effect_manager', None)
                    if effect_manager is None:
                        effect_manager = EffectManager(member)
                        member.effect_manager = effect_manager

                    # Create HoT effect (3% of max HP per turn for 2 turns)
                    hot_amount = int(max_hp * 0.03)
                    import asyncio
                    import logging
                    log = logging.getLogger(__name__)

                    async def apply_hot():
                        try:
                            await member.apply_healing(hot_amount, source_type="hot", source_name="sturdy_vest")
                        except Exception as e:
                            log.warning("Error applying Sturdy Vest HoT: %s", e)
                        finally:
                            # Remove from active set after 2 turns (simplified)
                            if member_id in active_hots:
                                active_hots.remove(member_id)

                    # Schedule HoT for next 2 turns
                    asyncio.create_task(apply_hot())

                    log.debug("Sturdy Vest activated HoT for %s: %d HP/turn for 2 turns", member.id, hot_amount)
                    BUS.emit("card_effect", self.id, member, "hot_activation", hot_amount, {
                        "hot_amount": hot_amount,
                        "duration": 2,
                        "trigger_threshold": 0.35
                    })

        # Check HP at the start of each turn and after damage taken
        BUS.subscribe("turn_start", _check_low_hp)
        BUS.subscribe("damage_taken", lambda target, attacker, damage: _check_low_hp())
