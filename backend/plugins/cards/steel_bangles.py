from dataclasses import dataclass
from dataclasses import field
import random

from autofighter.stats import BUS
from plugins.cards._base import CardBase


@dataclass
class SteelBangles(CardBase):
    id: str = "steel_bangles"
    name: str = "Steel Bangles"
    stars: int = 1
    effects: dict[str, float] = field(default_factory=lambda: {"mitigation": 0.03})
    about: str = "+3% Mitigation; On attack hit, 5% chance to reduce the target's next attack damage by 3%"

    async def apply(self, party) -> None:  # type: ignore[override]
        await super().apply(party)

        # Track targets that have damage reduction applied
        damage_reduced_targets = {}

        def _on_damage_dealt(attacker, target, damage, damage_type, source, source_action, action_name):
            # Check if attacker is one of our party members and this is an attack
            if attacker in party.members and action_name == "attack":
                # 5% chance to reduce target's next attack damage by 3%
                if random.random() < 0.05:
                    target_id = id(target)
                    damage_reduced_targets[target_id] = 0.03  # 3% damage reduction

                    import logging
                    log = logging.getLogger(__name__)
                    log.debug("Steel Bangles damage reduction applied to %s", getattr(target, 'id', 'unknown'))
                    BUS.emit("card_effect", self.id, attacker, "damage_reduction_applied", 3, {
                        "damage_reduction": 3,
                        "target": getattr(target, 'id', 'unknown'),
                        "trigger_chance": 0.05
                    })

        def _on_before_damage(target, attacker, damage):
            # Check if the attacker has damage reduction applied
            if attacker:
                attacker_id = id(attacker)
                if attacker_id in damage_reduced_targets:
                    reduction = damage_reduced_targets.pop(attacker_id)
                    reduced_damage = int(damage * (1 - reduction))
                    damage_reduction = damage - reduced_damage

                    import logging
                    log = logging.getLogger(__name__)
                    log.debug(
                        "Steel Bangles reducing attack damage from %d to %d",
                        damage,
                        reduced_damage,
                    )
                    BUS.emit(
                        "card_effect",
                        self.id,
                        attacker,
                        "damage_reduced",
                        damage_reduction,
                        {
                            "damage_reduction": damage_reduction,
                            "original_damage": damage,
                        },
                    )
                    return reduced_damage

            return damage

        BUS.subscribe("damage_dealt", _on_damage_dealt)
        BUS.subscribe("before_damage", _on_before_damage)
