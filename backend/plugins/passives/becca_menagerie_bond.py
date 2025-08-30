from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class BeccaMenagerieBond:
    """Becca's Menagerie Bond passive - jellyfish summoning and spirit bonuses."""
    plugin_type = "passive"
    id = "becca_menagerie_bond"
    name = "Menagerie Bond"
    trigger = "action_taken"  # Triggers when Becca acts
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of summon state and spirit bonuses
    _active_summon: ClassVar[dict[int, str]] = {}  # entity_id -> summon_type
    _summon_cooldown: ClassVar[dict[int, int]] = {}  # entity_id -> turns_remaining
    _spirit_stacks: ClassVar[dict[int, int]] = {}  # entity_id -> spirit_count
    _last_summon: ClassVar[dict[int, str]] = {}  # entity_id -> last_summon_type

    # Available jellyfish types (simplified)
    JELLYFISH_TYPES = ["healing", "electric", "poison", "shielding"]

    async def apply(self, target: "Stats") -> None:
        """Apply Becca's Menagerie Bond mechanics."""
        entity_id = id(target)

        # Initialize tracking if not present
        if entity_id not in self._summon_cooldown:
            self._summon_cooldown[entity_id] = 0
            self._spirit_stacks[entity_id] = 0
            self._active_summon[entity_id] = None

        # Apply spirit bonuses from previous summons
        current_spirit_stacks = self._spirit_stacks[entity_id]
        if current_spirit_stacks > 0:
            # +5% attack and defense per spirit stack
            spirit_attack_bonus = int(target.atk * 0.05 * current_spirit_stacks)
            spirit_defense_bonus = int(target.defense * 0.05 * current_spirit_stacks)

            spirit_effect = StatEffect(
                name=f"{self.id}_spirit_bonuses",
                stat_modifiers={
                    "atk": spirit_attack_bonus,
                    "defense": spirit_defense_bonus,
                },
                duration=-1,  # Permanent for rest of encounter
                source=self.id,
            )
            target.add_effect(spirit_effect)

            # Apply same bonuses to active pet if present
            if self._active_summon[entity_id]:
                pet_effect = StatEffect(
                    name=f"{self.id}_pet_spirit_bonuses",
                    stat_modifiers={
                        "atk": spirit_attack_bonus,
                        "defense": spirit_defense_bonus,
                    },
                    duration=-1,  # Permanent for rest of encounter
                    source=self.id,
                )
                # In full implementation, this would be applied to the actual summon entity
                target.add_effect(pet_effect)

        # Handle summon cooldown
        if self._summon_cooldown[entity_id] > 0:
            self._summon_cooldown[entity_id] -= 1

    async def summon_jellyfish(self, target: "Stats", jellyfish_type: str = None) -> bool:
        """Summon a jellyfish by spending 10% current HP."""
        entity_id = id(target)

        # Check cooldown
        if self._summon_cooldown[entity_id] > 0:
            return False

        # Check HP cost (10% of current HP)
        hp_cost = int(target.hp * 0.1)
        if target.hp <= hp_cost:
            return False  # Not enough HP

        # Pay HP cost
        target.hp -= hp_cost

        # If changing jellyfish type, previous one becomes a spirit
        if self._active_summon[entity_id] and jellyfish_type != self._active_summon[entity_id]:
            await self._create_spirit(target)

        # Select jellyfish type if not specified
        if jellyfish_type is None:
            import random
            jellyfish_type = random.choice(self.JELLYFISH_TYPES)

        # Create new summon
        self._active_summon[entity_id] = jellyfish_type
        self._last_summon[entity_id] = jellyfish_type
        self._summon_cooldown[entity_id] = 1  # One turn cooldown

        # Create summon with 50% of Becca's base stats
        summon_stats = {
            "hp": int(target.max_hp * 0.5),
            "atk": int(target.atk * 0.5),
            "defense": int(target.defense * 0.5),
        }

        # Apply summon-specific effects (simplified)
        await self._apply_summon_effects(target, jellyfish_type, summon_stats)

        return True

    async def _create_spirit(self, target: "Stats") -> None:
        """Create a spirit from the previous summon."""
        entity_id = id(target)
        self._spirit_stacks[entity_id] += 1

        # Remove active summon
        self._active_summon[entity_id] = None

    async def _apply_summon_effects(self, target: "Stats", jellyfish_type: str, stats: dict) -> None:
        """Apply summon-specific effects based on jellyfish type."""
        # Create a general summon effect (in full implementation, would create actual summon entity)
        summon_effect = StatEffect(
            name=f"{self.id}_active_summon_{jellyfish_type}",
            stat_modifiers={
                "summon_atk": stats["atk"],
                "summon_hp": stats["hp"],
                "summon_defense": stats["defense"],
            },
            duration=-1,  # Until summon is replaced or defeated
            source=self.id,
        )
        target.add_effect(summon_effect)

    async def on_summon_defeat(self, target: "Stats") -> None:
        """Handle summon defeat - still creates a spirit."""
        entity_id = id(target)
        if self._active_summon[entity_id]:
            await self._create_spirit(target)

    @classmethod
    def get_active_summon(cls, target: "Stats") -> str:
        """Get current active summon type."""
        return cls._active_summon.get(id(target), None)

    @classmethod
    def get_spirit_stacks(cls, target: "Stats") -> int:
        """Get current spirit stack count."""
        return cls._spirit_stacks.get(id(target), 0)

    @classmethod
    def get_cooldown(cls, target: "Stats") -> int:
        """Get remaining summon cooldown."""
        return cls._summon_cooldown.get(id(target), 0)
