from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from autofighter.summons import SummonManager
from plugins.cards._base import CardBase


@dataclass
class PhantomAlly(CardBase):
    id: str = "phantom_ally"
    name: str = "Phantom Ally"
    stars: int = 5
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 15.0})
    about: str = (
        "+1500% ATK; on the first turn, summon a temporary copy of a random ally."
    )

    async def apply(self, party):
        await super().apply(party)
        if not party.members:
            return

        # Choose a random ally to create a phantom of
        original = random.choice(party.members)

        # Create phantom using the new summons system
        # Phantoms are full-strength copies (multiplier=1.0) but temporary (1 turn)
        summon = SummonManager.create_summon(
            summoner=original,
            summon_type="phantom",
            source=self.id,
            stat_multiplier=1.0,  # Full strength copy
            turns_remaining=1,  # Only lasts one turn
            max_summons=1,
        )

        if summon:
            # Add the summon to the party for this battle
            party.members.append(summon)

            # Track phantom ally summoning
            BUS.emit("card_effect", "phantom_ally", original, "phantom_summoned", 1, {
                "original_ally": getattr(original, 'id', str(original)),
                "phantom_id": summon.id,
                "phantom_stats": {
                    "hp": summon.hp,
                    "max_hp": summon.max_hp,
                    "atk": summon.atk,
                    "defense": summon.defense
                },
                "atk_bonus_applied": 1500
            })

            # Register cleanup handler to remove from party when battle ends
            def _cleanup(_entity):
                if summon in party.members:
                    party.members.remove(summon)
                    # Track phantom cleanup
                    BUS.emit("card_effect", "phantom_ally", summon, "phantom_dismissed", 1, {
                        "reason": "battle_end",
                        "original_ally": getattr(original, 'id', str(original))
                    })
                BUS.unsubscribe("battle_end", _cleanup)

            BUS.subscribe("battle_end", _cleanup)
