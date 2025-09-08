from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class AllyOverload:
    """Ally's Overload passive - twin dagger stance system with charge mechanics."""
    plugin_type = "passive"
    id = "ally_overload"
    name = "Overload"
    trigger = "action_taken"  # Triggers when Ally takes any action
    max_stacks = 120  # Soft cap - show charge level with diminished returns past 120
    stack_display = "number"

    # Class-level tracking of overload charge and stance for each entity
    _overload_charge: ClassVar[dict[int, int]] = {}
    _overload_active: ClassVar[dict[int, bool]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply Ally's twin dagger and overload mechanics."""
        entity_id = id(target)

        # Initialize if not present
        if entity_id not in self._overload_charge:
            self._overload_charge[entity_id] = 0
            self._overload_active[entity_id] = False

        # Twin daggers - always grants two attacks per action
        if not self._overload_active[entity_id]:
            target.actions_per_turn = 2

        # Build 10 Overload charge per pair of strikes
        base_charge_gain = 10

        # Soft cap: past 120, gain charge at reduced rate (50% effectiveness)
        current_charge = self._overload_charge[entity_id]
        if current_charge > 120:
            charge_gain = base_charge_gain * 0.5  # Diminished returns
        else:
            charge_gain = base_charge_gain

        self._overload_charge[entity_id] += charge_gain

        # Check if Overload can be triggered (100+ charge)
        current_charge = self._overload_charge[entity_id]
        if current_charge >= 100 and not self._overload_active[entity_id]:
            # Can activate Overload stance
            await self._activate_overload(target)

        # Handle charge decay when stance is inactive
        if not self._overload_active[entity_id]:
            self._overload_charge[entity_id] = max(0, current_charge - 5)

    async def _activate_overload(self, target: "Stats") -> None:
        """Activate Overload stance."""
        entity_id = id(target)
        self._overload_active[entity_id] = True

        # Double attack count
        target.actions_per_turn = 4  # 2 base * 2 = 4

        # +30% damage bonus
        damage_bonus = StatEffect(
            name=f"{self.id}_damage_bonus",
            stat_modifiers={"atk": int(target.atk * 0.3)},
            duration=-1,  # Active while Overload is on
            source=self.id,
        )
        target.add_effect(damage_bonus)

        # +40% damage taken vulnerability
        damage_vulnerability = StatEffect(
            name=f"{self.id}_damage_vulnerability",
            stat_modifiers={"mitigation": -0.4},  # Reduce mitigation by 40%
            duration=-1,  # Active while Overload is on
            source=self.id,
        )
        target.add_effect(damage_vulnerability)

        # Block HoT ticks (would need integration with effect system)
        hot_block = StatEffect(
            name=f"{self.id}_hot_block",
            stat_modifiers={"effect_resistance": 1.0},  # 100% resistance to beneficial effects
            duration=-1,  # Active while Overload is on
            source=self.id,
        )
        target.add_effect(hot_block)

        # Cap recoverable HP at 20% of normal
        max_recoverable_hp = int(target.max_hp * 0.2)
        hp_cap = StatEffect(
            name=f"{self.id}_hp_cap",
            stat_modifiers={"max_hp": max_recoverable_hp - target.max_hp},  # Reduce max recoverable
            duration=-1,  # Active while Overload is on
            source=self.id,
        )
        target.add_effect(hp_cap)

    async def _deactivate_overload(self, target: "Stats") -> None:
        """Deactivate Overload stance."""
        entity_id = id(target)
        self._overload_active[entity_id] = False

        # Remove all Overload effects
        effects_to_remove = [
            f"{self.id}_damage_bonus",
            f"{self.id}_damage_vulnerability",
            f"{self.id}_hot_block",
            f"{self.id}_hp_cap"
        ]

        for effect_name in effects_to_remove:
            # Use effect manager helper to remove by name
            target.remove_effect_by_name(effect_name)

        # Reset to base twin dagger attacks
        target.actions_per_turn = 2

    async def on_turn_end(self, target: "Stats") -> None:
        """Handle end-of-turn Overload mechanics."""
        entity_id = id(target)

        # Initialize if not present
        if entity_id not in self._overload_charge:
            self._overload_charge[entity_id] = 0
            self._overload_active[entity_id] = False

        if self._overload_active[entity_id]:
            # Drain 20 charge per turn while active
            self._overload_charge[entity_id] = max(0, self._overload_charge[entity_id] - 20)

            # Check if charge is depleted
            if self._overload_charge[entity_id] <= 0:
                await self._deactivate_overload(target)

    async def on_defeat(self, target: "Stats") -> None:
        """Handle Overload deactivation on defeat."""
        entity_id = id(target)

        # Initialize if not present
        if entity_id not in self._overload_charge:
            self._overload_charge[entity_id] = 0
            self._overload_active[entity_id] = False

        if self._overload_active[entity_id]:
            await self._deactivate_overload(target)

    @classmethod
    def get_charge(cls, target: "Stats") -> int:
        """Get current Overload charge."""
        return cls._overload_charge.get(id(target), 0)

    @classmethod
    def is_overload_active(cls, target: "Stats") -> bool:
        """Check if Overload stance is active."""
        return cls._overload_active.get(id(target), False)

    @classmethod
    def get_stacks(cls, target: "Stats") -> int:
        """Return current overload charge for UI display."""
        return cls._overload_charge.get(id(target), 0)
