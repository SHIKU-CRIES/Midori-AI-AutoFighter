from dataclasses import dataclass


@dataclass
class RoomHeal:
    plugin_type = "passive"
    id = "room_heal"
    name = "Room Heal"
    trigger = "battle_end"
    amount = 1

    async def apply(self, target, **kwargs) -> None:
        # Support monkeypatching: if class attribute differs from original default, use class attribute
        heal_amount = type(self).amount if type(self).amount != 1 else self.amount
        await target.apply_healing(heal_amount)
