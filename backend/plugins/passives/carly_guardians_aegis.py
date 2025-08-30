from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class CarlyGuardiansAegis:
    """Carly's Guardian's Aegis passive - tank mechanics with healing and mitigation."""
    plugin_type = "passive"
    id = "carly_guardians_aegis"
    name = "Guardian's Aegis"
    trigger = "turn_start"  # Triggers at start of turn for healing
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of mitigation stacks gained from being hit
    _mitigation_stacks: ClassVar[dict[int, int]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply Carly's Guardian's Aegis healing mechanics."""
        entity_id = id(target)

        # Initialize mitigation stack tracking if not present
        if entity_id not in self._mitigation_stacks:
            self._mitigation_stacks[entity_id] = 0

        # Heal the most injured ally each turn
        # This would need party system integration to find allies
        # For now, apply a small self-heal based on defense
        defense_based_heal = int(target.defense * 0.1)

        heal_effect = StatEffect(
            name=f"{self.id}_defense_heal",
            stat_modifiers={"hp": defense_based_heal},
            duration=1,  # One turn healing
            source=self.id,
        )
        target.add_effect(heal_effect)

        # Apply accumulated mitigation stacks from previous hits
        if self._mitigation_stacks[entity_id] > 0:
            mitigation_bonus = self._mitigation_stacks[entity_id] * 0.02  # 2% per stack

            mitigation_effect = StatEffect(
                name=f"{self.id}_mitigation_stacks",
                stat_modifiers={"mitigation": mitigation_bonus},
                duration=-1,  # Permanent for rest of fight
                source=self.id,
            )
            target.add_effect(mitigation_effect)

    async def on_damage_taken(self, target: "Stats", attacker: "Stats", damage: int) -> None:
        """Handle Carly's damage mitigation mechanics when hit."""
        entity_id = id(target)

        # Apply mitigation twice (square mitigation)
        # This would need integration with damage calculation system
        # For now, apply a temporary defensive bonus
        squared_mitigation_bonus = target.mitigation * 0.1  # 10% bonus mitigation

        double_mitigation_effect = StatEffect(
            name=f"{self.id}_squared_mitigation",
            stat_modifiers={"mitigation": squared_mitigation_bonus},
            duration=1,  # For this hit only
            source=self.id,
        )
        target.add_effect(double_mitigation_effect)

        # Gain two mitigation stacks for rest of fight
        self._mitigation_stacks[entity_id] += 2

        # Apply taunt effect (force enemies to target Carly)
        # This would need battle system integration
        taunt_effect = StatEffect(
            name=f"{self.id}_taunt",
            stat_modifiers={"taunt_level": 1.0},  # High priority target
            duration=2,  # Two turns of taunt
            source=self.id,
        )
        target.add_effect(taunt_effect)

    async def on_ultimate_use(self, target: "Stats", allies: list["Stats"]) -> None:
        """Handle ultimate ability effects - grant mitigation to allies."""
        # Grant all allies mitigation equal to half of Carly's own
        mitigation_to_share = target.mitigation * 0.5

        for ally in allies:
            if ally != target:  # Don't apply to self
                ally_mitigation_effect = StatEffect(
                    name=f"{self.id}_shared_mitigation",
                    stat_modifiers={"mitigation": mitigation_to_share},
                    duration=3,  # Three turns
                    source=self.id,
                )
                ally.add_effect(ally_mitigation_effect)

        # Reduce Carly's mitigation by the same amount
        mitigation_reduction_effect = StatEffect(
            name=f"{self.id}_mitigation_reduction",
            stat_modifiers={"mitigation": -mitigation_to_share},
            duration=3,  # Three turns
            source=self.id,
        )
        target.add_effect(mitigation_reduction_effect)

    @classmethod
    def get_mitigation_stacks(cls, target: "Stats") -> int:
        """Get current mitigation stacks for an entity."""
        return cls._mitigation_stacks.get(id(target), 0)
