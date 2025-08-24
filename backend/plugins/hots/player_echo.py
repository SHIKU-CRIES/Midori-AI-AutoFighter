from autofighter.effects import HealingOverTime
from plugins.damage_types.generic import Generic
from plugins.damage_types._base import DamageTypeBase


class PlayerEcho(HealingOverTime):
    plugin_type = "hot"
    id = "player_echo"
    damage_type: DamageTypeBase = Generic()

    def __init__(self, player_name: str, healing: int, turns: int) -> None:
        super().__init__(f"{player_name}'s Echo", healing, turns, self.id)

    async def tick(self, target, damage=0, *_):
        await target.apply_healing(int(damage * 0.2))
        self.turns -= 1
        return self.turns > 0
