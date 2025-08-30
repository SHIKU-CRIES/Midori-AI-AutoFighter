from dataclasses import dataclass
import random
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class KboshiFluxCycle:
    """Kboshi's Flux Cycle passive - random element switching with bonuses."""
    plugin_type = "passive"
    id = "kboshi_flux_cycle"
    name = "Flux Cycle"
    trigger = "turn_start"  # Triggers at start of Kboshi's turn
    max_stacks = 1  # Only one instance per character

    # Track accumulated damage bonuses and HoT stacks per entity
    _damage_stacks: ClassVar[dict[int, int]] = {}
    _hot_stacks: ClassVar[dict[int, int]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply Flux Cycle element switching mechanics for Kboshi."""
        entity_id = id(target)

        # Initialize tracking if needed
        if entity_id not in self._damage_stacks:
            self._damage_stacks[entity_id] = 0
            self._hot_stacks[entity_id] = 0

        # High chance to switch to random damage type
        if random.random() < 0.8:  # 80% chance to switch
            # Element successfully changed - remove accumulated stacks and apply mitigation debuff
            if self._damage_stacks[entity_id] > 0 or self._hot_stacks[entity_id] > 0:
                # Remove existing bonus effects
                target._active_effects = [
                    effect for effect in target._active_effects
                    if not effect.name.startswith(f"{self.id}_damage_bonus") and
                       not effect.name.startswith(f"{self.id}_hot_heal")
                ]

                # Apply brief mitigation debuff to all foes (would need foe access)
                # For now, just reset stacks
                self._damage_stacks[entity_id] = 0
                self._hot_stacks[entity_id] = 0

            # Switch damage type (would need damage type system integration)
            # For now, just indicate successful switch
            pass
        else:
            # Element failed to change - gain damage bonus and HoT
            self._damage_stacks[entity_id] += 1
            self._hot_stacks[entity_id] += 1

            # Apply 20% damage bonus per stack
            damage_bonus = StatEffect(
                name=f"{self.id}_damage_bonus_{self._damage_stacks[entity_id]}",
                stat_modifiers={"atk": int(target.atk * 0.2)},
                duration=-1,  # Until element changes
                source=self.id,
            )
            target.add_effect(damage_bonus)

            # Apply small HoT for that turn
            hot_heal = StatEffect(
                name=f"{self.id}_hot_heal_{self._hot_stacks[entity_id]}",
                stat_modifiers={},  # Would need HoT integration
                duration=1,  # One turn
                source=self.id,
            )
            target.add_effect(hot_heal)

    @classmethod
    def get_damage_stacks(cls, target: "Stats") -> int:
        """Get current damage bonus stacks."""
        return cls._damage_stacks.get(id(target), 0)

    @classmethod
    def get_hot_stacks(cls, target: "Stats") -> int:
        """Get current HoT stacks."""
        return cls._hot_stacks.get(id(target), 0)
