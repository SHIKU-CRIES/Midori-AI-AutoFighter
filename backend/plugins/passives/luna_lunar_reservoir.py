from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class LunaLunarReservoir:
    """Luna's Lunar Reservoir passive - charge-based system that scales attack count."""
    plugin_type = "passive"
    id = "luna_lunar_reservoir"
    name = "Lunar Reservoir"
    trigger = "action_taken"  # Triggers when Luna takes any action
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of charge points for each entity
    _charge_points: ClassVar[dict[int, int]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply charge mechanics for Luna."""
        entity_id = id(target)

        # Initialize charge if not present
        if entity_id not in self._charge_points:
            self._charge_points[entity_id] = 0

        # Grant 1 charge point per action
        self._charge_points[entity_id] += 1
        current_charge = self._charge_points[entity_id]

        # Cap at 200 charge points
        if current_charge > 200:
            self._charge_points[entity_id] = 200
            current_charge = 200

        # Determine attack count based on charge level
        if current_charge < 35:
            target.actions_per_turn = 2
        elif current_charge < 50:
            target.actions_per_turn = 4
        elif current_charge < 70:
            target.actions_per_turn = 8
        elif current_charge < 85:
            target.actions_per_turn = 16
        else:  # 85+ charge
            target.actions_per_turn = 32

        # Handle boosted mode (200+ charge)
        if current_charge >= 200:
            # In boosted mode, spend 50 charge per turn
            self._charge_points[entity_id] = max(0, current_charge - 50)

    @classmethod
    def get_charge(cls, target: "Stats") -> int:
        """Get current charge points for an entity."""
        return cls._charge_points.get(id(target), 0)

    @classmethod
    def add_charge(cls, target: "Stats", amount: int = 1) -> None:
        """Add charge points (for external effects)."""
        entity_id = id(target)
        if entity_id not in cls._charge_points:
            cls._charge_points[entity_id] = 0

        cls._charge_points[entity_id] = min(200, cls._charge_points[entity_id] + amount)
