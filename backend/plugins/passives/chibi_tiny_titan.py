from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class ChibiTinyTitan:
    """Chibi's Tiny Titan passive - 4x Vitality HP gain and 500% Vitality to attack conversion."""
    plugin_type = "passive"
    id = "chibi_tiny_titan"
    name = "Tiny Titan"
    trigger = "damage_taken"  # Triggers when Chibi takes damage to increase Vitality
    max_stacks = 1  # Only one instance per character

    # Class-level tracking of accumulated Vitality bonuses
    _vitality_bonuses: ClassVar[dict[int, float]] = {}

    async def apply(self, target: "Stats") -> None:
        """Apply Chibi's Tiny Titan mechanics."""
        entity_id = id(target)

        # Initialize vitality bonus tracking if not present
        if entity_id not in self._vitality_bonuses:
            self._vitality_bonuses[entity_id] = 0.0

        # When hit, increase Vitality by 0.01 for the rest of battle
        self._vitality_bonuses[entity_id] += 0.01

        # Apply 4x HP gain from Vitality
        # Assuming Vitality translates to max HP bonus
        vitality_hp_bonus = int(self._vitality_bonuses[entity_id] * 4 * target.max_hp)

        hp_effect = StatEffect(
            name=f"{self.id}_vitality_hp",
            stat_modifiers={"max_hp": vitality_hp_bonus},
            duration=-1,  # Permanent for rest of battle
            source=self.id,
        )
        target.add_effect(hp_effect)

        # Convert 500% of current Vitality into attack
        vitality_attack_bonus = int(self._vitality_bonuses[entity_id] * 5 * target.atk)

        attack_effect = StatEffect(
            name=f"{self.id}_vitality_attack",
            stat_modifiers={"atk": vitality_attack_bonus},
            duration=-1,  # Permanent for rest of battle
            source=self.id,
        )
        target.add_effect(attack_effect)

        # Apply damage reduction from Vitality bonus
        damage_reduction = self._vitality_bonuses[entity_id] * 0.05  # 5% per 0.01 Vitality
        mitigation_effect = StatEffect(
            name=f"{self.id}_vitality_mitigation",
            stat_modifiers={"mitigation": damage_reduction},
            duration=-1,  # Permanent for rest of battle
            source=self.id,
        )
        target.add_effect(mitigation_effect)

    async def on_turn_end(self, target: "Stats") -> None:
        """Apply minor HoT each turn while Vitality bonus is active."""
        entity_id = id(target)
        vitality_bonus = self._vitality_bonuses.get(entity_id, 0.0)

        if vitality_bonus > 0:
            # Minor HoT based on Vitality bonus
            hot_amount = int(vitality_bonus * target.max_hp * 0.02)  # 2% of max HP per 0.01 Vitality
            if hot_amount > 0:
                target.hp = min(target.max_hp, target.hp + hot_amount)

    @classmethod
    def get_vitality_bonus(cls, target: "Stats") -> float:
        """Get current Vitality bonus for an entity."""
        return cls._vitality_bonuses.get(id(target), 0.0)
