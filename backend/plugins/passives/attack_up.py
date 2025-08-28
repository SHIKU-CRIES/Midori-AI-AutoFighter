from dataclasses import dataclass

from autofighter.stats import StatEffect


@dataclass
class AttackUp:
    plugin_type = "passive"
    id = "attack_up"
    name = "Attack Up"
    trigger = "battle_start"
    amount = 5

    async def apply(self, target) -> None:
        effect = StatEffect(
            name=f"{self.id}_atk_up",
            stat_modifiers={"atk": self.amount},
            source=self.id,
        )
        target.add_effect(effect)
