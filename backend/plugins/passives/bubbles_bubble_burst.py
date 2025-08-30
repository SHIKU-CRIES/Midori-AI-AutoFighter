from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class BubblesBubbleBurst:
    """Bubbles' Bubble Burst passive - random element with area damage."""
    plugin_type = "passive"
    id = "bubbles_bubble_burst"
    name = "Bubble Burst"
    trigger = "turn_start"  # Triggers at start of Bubbles' turn
    max_stacks = 1  # Only one instance per character

    # Track bubble stacks per enemy target
    _bubble_stacks: ClassVar[dict[int, dict[int, int]]] = {}  # bubbles_id -> {target_id -> stacks}

    async def apply(self, target: "Stats") -> None:
        """Apply Bubbles' random element switching mechanics."""
        # Switch damage type randomly each turn
        # This would need damage type system integration
        pass

    async def on_hit_enemy(self, bubbles: "Stats", enemy: "Stats") -> None:
        """Apply bubble stack when hitting an enemy."""
        bubbles_id = id(bubbles)
        enemy_id = id(enemy)

        # Initialize tracking
        if bubbles_id not in self._bubble_stacks:
            self._bubble_stacks[bubbles_id] = {}
        if enemy_id not in self._bubble_stacks[bubbles_id]:
            self._bubble_stacks[bubbles_id][enemy_id] = 0

        # Add bubble stack
        self._bubble_stacks[bubbles_id][enemy_id] += 1

        # Check if we've reached 3 stacks for area burst
        if self._bubble_stacks[bubbles_id][enemy_id] >= 3:
            await self._trigger_bubble_burst(bubbles, enemy)

    async def _trigger_bubble_burst(self, bubbles: "Stats", trigger_enemy: "Stats") -> None:
        """Trigger bubble burst area damage and effects."""
        bubbles_id = id(bubbles)
        trigger_enemy_id = id(trigger_enemy)

        # Reset bubble stacks for this enemy
        if bubbles_id in self._bubble_stacks and trigger_enemy_id in self._bubble_stacks[bubbles_id]:
            self._bubble_stacks[bubbles_id][trigger_enemy_id] = 0

        # Grant Bubbles permanent +10% attack buff
        attack_buff = StatEffect(
            name=f"{self.id}_burst_bonus_{len([e for e in bubbles._active_effects if 'burst_bonus' in e.name])}",
            stat_modifiers={"atk": int(bubbles.atk * 0.1)},
            duration=-1,  # Permanent
            source=self.id,
        )
        bubbles.add_effect(attack_buff)

        # Area damage and DoT would need battle system integration
        # This would deal damage to all combatants and apply DoT to enemies

    @classmethod
    def get_bubble_stacks(cls, bubbles: "Stats", enemy: "Stats") -> int:
        """Get current bubble stacks on a specific enemy."""
        bubbles_id = id(bubbles)
        enemy_id = id(enemy)

        if bubbles_id not in cls._bubble_stacks:
            return 0
        return cls._bubble_stacks[bubbles_id].get(enemy_id, 0)
