from dataclasses import dataclass
import random
from typing import TYPE_CHECKING
from typing import ClassVar
from weakref import WeakKeyDictionary

from autofighter.stats import BUS
from autofighter.stats import StatEffect
from plugins.effects.aftertaste import Aftertaste
from plugins.relics._base import safe_async_task

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class HilanderCriticalFerment:
    """Hilander's Critical Ferment passive - builds crit rate/damage, consumes on crit."""
    plugin_type = "passive"
    id = "hilander_critical_ferment"
    name = "Critical Ferment"
    trigger = "hit_landed"  # Triggers when Hilander lands a hit
    stack_display = "pips"  # Unlimited stacks with numeric fallback past five
    _subscribed: ClassVar[WeakKeyDictionary["Stats", bool]] = WeakKeyDictionary()

    async def apply(self, target: "Stats") -> None:
        """Apply crit building mechanics for Hilander."""
        # Build 5% crit rate and 10% crit damage each hit

        # Count existing ferment stacks
        ferment_stacks = sum(
            1
            for effect in target._active_effects
            if effect.name.startswith(f"{self.id}_crit_stack") and effect.name.endswith("_rate")
        )

        if ferment_stacks >= 20:
            chance = max(0.01, 1 - 0.05 * (ferment_stacks - 19))
            if random.random() >= chance:
                return

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

        if not self._subscribed.get(target):
            def _crit(attacker, crit_target, damage, *_args) -> None:
                if attacker is target:
                    self.on_critical_hit(attacker, crit_target, damage)

            BUS.subscribe("critical_hit", _crit)
            target._hilander_crit_cb = _crit
            self._subscribed[target] = True
    @classmethod
    def on_critical_hit(cls, attacker: "Stats", target: "Stats", damage: int) -> None:
        """Handle critical hit - unleash Aftertaste and consume one stack."""
        base = int(damage * 0.25)
        if base > 0:
            effect = Aftertaste(base_pot=base)
            safe_async_task(effect.apply(attacker, target))

        ferment_effects = [
            effect
            for effect in attacker._active_effects
            if effect.name.startswith(f"{cls.id}_crit_stack")
        ]

        if ferment_effects:
            highest_stack = 0

            for effect in ferment_effects:
                try:
                    parts = effect.name.rsplit("_", 3)
                    stack_num = int(parts[2])
                    if stack_num > highest_stack:
                        highest_stack = stack_num
                except (IndexError, ValueError):
                    continue

            attacker._active_effects = [
                effect
                for effect in attacker._active_effects
                if not (
                    effect.name == f"{cls.id}_crit_stack_{highest_stack}_rate"
                    or effect.name == f"{cls.id}_crit_stack_{highest_stack}_damage"
                )
            ]

    @classmethod
    def get_stacks(cls, target: "Stats") -> int:
        """Return current ferment stacks for Hilander."""
        return sum(
            1
            for effect in getattr(target, "_active_effects", [])
            if effect.name.startswith(f"{cls.id}_crit_stack_") and effect.name.endswith("_rate")
        )
