from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class LadyFireAndIceDualityEngine:
    """Lady Fire and Ice's Duality Engine passive - elemental flux system."""
    plugin_type = "passive"
    id = "lady_fire_and_ice_duality_engine"
    name = "Duality Engine"
    trigger = "action_taken"  # Triggers when Lady Fire and Ice attacks
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of last element used and flux stacks
    _last_element: ClassVar[dict[int, str]] = {}
    _flux_stacks: ClassVar[dict[int, int]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply Lady Fire and Ice's duality mechanics."""
        entity_id = id(target)

        # Initialize tracking if not present
        if entity_id not in self._last_element:
            self._last_element[entity_id] = None
            self._flux_stacks[entity_id] = 0

        # Determine current element (would need damage type integration)
        # For now, assume we can detect if this is fire or ice
        current_element = self._determine_current_element(target)

        # Check if alternating or using same element twice
        if self._last_element[entity_id] is not None:
            if current_element != self._last_element[entity_id]:
                # Alternating elements - gain Elemental Flux stack
                await self._gain_flux_stack(target)
            else:
                # Same element twice - consume all stacks for effects
                await self._consume_flux_stacks(target)

        # Update last element used
        self._last_element[entity_id] = current_element

    def _determine_current_element(self, target: "Stats") -> str:
        """Determine current element being used (simplified)."""
        # This would normally check the actual damage type
        # For now, alternate randomly between fire and ice
        import random
        return random.choice(["fire", "ice"])

    async def _gain_flux_stack(self, target: "Stats") -> None:
        """Gain an Elemental Flux stack."""
        entity_id = id(target)
        self._flux_stacks[entity_id] += 1

        # Apply 5% boost to burn DoT and chill debuff potency per stack
        current_stacks = self._flux_stacks[entity_id]
        potency_bonus = current_stacks * 0.05

        flux_effect = StatEffect(
            name=f"{self.id}_flux_potency",
            stat_modifiers={
                "burn_potency": potency_bonus,
                "chill_potency": potency_bonus,
            },
            duration=-1,  # Permanent until consumed
            source=self.id,
        )
        target.add_effect(flux_effect)

    async def _consume_flux_stacks(self, target: "Stats") -> None:
        """Consume all flux stacks for beneficial effects."""
        entity_id = id(target)
        stacks_to_consume = self._flux_stacks[entity_id]

        if stacks_to_consume > 0:
            # Apply small HoT to allies (would need party system integration)
            ally_hot_amount = stacks_to_consume * 10  # 10 HP per stack

            ally_hot_effect = StatEffect(
                name=f"{self.id}_flux_ally_hot",
                stat_modifiers={"hp": ally_hot_amount},
                duration=3,  # Three turns of HoT
                source=self.id,
            )
            # This would be applied to all allies in actual implementation
            target.add_effect(ally_hot_effect)

            # Apply mitigation debuff to foes (would need enemy targeting)
            # In full implementation, would apply 2% mitigation reduction per stack to enemies

            # Remove flux potency bonus effects
            target._active_effects = [
                effect for effect in target._active_effects
                if effect.name != f"{self.id}_flux_potency"
            ]

            # Reset flux stacks
            self._flux_stacks[entity_id] = 0

    @classmethod
    def get_flux_stacks(cls, target: "Stats") -> int:
        """Get current flux stacks for an entity."""
        return cls._flux_stacks.get(id(target), 0)

    @classmethod
    def get_last_element(cls, target: "Stats") -> str:
        """Get last element used by an entity."""
        return cls._last_element.get(id(target), None)
