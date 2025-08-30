from dataclasses import dataclass
from typing import TYPE_CHECKING

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class HilanderCriticalFerment:
    """Hilander's Critical Ferment passive - builds crit rate/damage, consumes on crit."""
    plugin_type = "passive"
    id = "hilander_critical_ferment"
    name = "Critical Ferment"
    trigger = "hit_landed"  # Triggers when Hilander lands a hit
    max_stacks = 1  # Only one instance per character

    async def apply(self, target: "Stats") -> None:
        """Apply crit building mechanics for Hilander."""
        # Build 5% crit rate and 10% crit damage each hit, stacking up to 20 times

        # Count existing ferment stacks
        ferment_stacks = sum(
            1 for effect in target._active_effects
            if effect.name.startswith(f"{self.id}_crit_stack")
        )

        if ferment_stacks < 20:  # Cap at 20 stacks
            # Add a new stack
            stack_id = ferment_stacks + 1
            crit_rate_bonus = StatEffect(
                name=f"{self.id}_crit_stack_{stack_id}_rate",
                stat_modifiers={"crit_rate": 0.05},  # +5% crit rate
                duration=-1,  # Permanent until consumed
                source=self.id,
            )
            target.add_effect(crit_rate_bonus)

            crit_damage_bonus = StatEffect(
                name=f"{self.id}_crit_stack_{stack_id}_damage",
                stat_modifiers={"crit_damage": 0.1},  # +10% crit damage
                duration=-1,  # Permanent until consumed
                source=self.id,
            )
            target.add_effect(crit_damage_bonus)

    async def on_critical_hit(self, target: "Stats") -> None:
        """Handle critical hit - unleash Aftertaste and consume one stack."""
        # Deal Aftertaste hit (25% of original damage with random element)
        # This would need integration with the actual damage system
        # For now, just consume one stack

        # Find and remove the most recent ferment stack
        ferment_effects = [
            effect for effect in target._active_effects
            if effect.name.startswith(f"{self.id}_crit_stack")
        ]

        if ferment_effects:
            # Remove the highest numbered stack (most recent)
            highest_stack = 0

            for effect in ferment_effects:
                # Extract stack number from effect name
                try:
                    parts = effect.name.split("_")
                    stack_num = int(parts[3])  # crit_stack_{NUM}_rate/damage
                    if stack_num > highest_stack:
                        highest_stack = stack_num
                except (IndexError, ValueError):
                    continue

            # Remove effects for the highest stack
            target._active_effects = [
                effect for effect in target._active_effects
                if not (effect.name == f"{self.id}_crit_stack_{highest_stack}_rate" or
                       effect.name == f"{self.id}_crit_stack_{highest_stack}_damage")
            ]
