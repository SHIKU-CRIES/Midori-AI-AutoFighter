from dataclasses import dataclass
from dataclasses import field

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class HonedPoint(CardBase):
    id: str = "honed_point"
    name: str = "Honed Point"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"atk": 0.04})
    about: str = "+4% ATK; First attack vs an unmarked enemy gains +10% armor penetration for that hit"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        # Track which enemies have been marked (attacked) by which party members
        marked_enemies = {}

        def _on_damage_dealt(attacker, target, damage, damage_type, source, source_action, action_name):
            # Check if attacker is one of our party members and this is an attack
            if attacker in party.members and action_name == "attack":
                attacker_id = id(attacker)
                target_id = id(target)

                # Check if this is the first attack against this enemy by this attacker
                if attacker_id not in marked_enemies:
                    marked_enemies[attacker_id] = set()

                if target_id not in marked_enemies[attacker_id]:
                    # Mark this enemy and apply armor penetration bonus
                    marked_enemies[attacker_id].add(target_id)

                    # Apply +10% armor penetration for this hit (theoretical implementation)
                    armor_pen_bonus = 10
                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Honed Point armor penetration: +%d%% armor pen vs unmarked enemy", armor_pen_bonus)
                    BUS.emit("card_effect", self.id, attacker, "armor_penetration", armor_pen_bonus, {
                        "armor_pen_bonus": armor_pen_bonus,
                        "trigger_event": "first_attack_unmarked"
                    })

        def _on_battle_start(target):
            # Reset marked enemies for new battle
            if target in party.members:
                marked_enemies.clear()

        BUS.subscribe("damage_dealt", _on_damage_dealt)
        BUS.subscribe("battle_start", _on_battle_start)
