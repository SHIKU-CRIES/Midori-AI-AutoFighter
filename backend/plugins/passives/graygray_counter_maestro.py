from dataclasses import dataclass
from typing import TYPE_CHECKING

from autofighter.stats import StatEffect

if TYPE_CHECKING:
    from autofighter.stats import Stats


@dataclass
class GraygrayCounterMaestro:
    """Graygray's Counter Maestro passive - retaliates after every hit taken."""
    plugin_type = "passive"
    id = "graygray_counter_maestro"
    name = "Counter Maestro"
    trigger = "damage_taken"  # Triggers when Graygray takes damage
    max_stacks = 1  # Only one instance per character

    async def apply(self, target: "Stats") -> None:
        """Apply counter-attack mechanics for Graygray."""
        # This will be called when Graygray takes damage
        # We need the attacker info, which should be passed via the event system

        # For now, implement the core mechanic - we'll need to extend this
        # when we have proper damage event handling

        # Grant +5% attack buff after counter
        attack_buff = StatEffect(
            name=f"{self.id}_attack_buff",
            stat_modifiers={"atk": int(target.atk * 0.05)},
            duration=1,  # One turn
            source=self.id,
        )
        target.add_effect(attack_buff)

        # Grant mitigation buff for one turn
        mitigation_buff = StatEffect(
            name=f"{self.id}_mitigation_buff",
            stat_modifiers={"mitigation": 0.1},  # 10% mitigation increase
            duration=1,  # One turn
            source=self.id,
        )
        target.add_effect(mitigation_buff)

    async def counter_attack(self, defender: "Stats", attacker: "Stats", damage_received: int) -> None:
        """Perform the actual counter attack."""
        if attacker is None:
            return

        # Deal 50% of damage received back to attacker
        counter_damage = int(damage_received * 0.5)

        # Use defender's current damage type for the counter
        await attacker.apply_damage(
            counter_damage,
            attacker=defender,
            trigger_on_hit=False,  # Avoid recursive triggers
            action_name="Counter Attack"
        )
