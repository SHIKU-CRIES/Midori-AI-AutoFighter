from dataclasses import dataclass


@dataclass
class RoomHeal:
    plugin_type = "passive"
    id = "room_heal"
    name = "Room Heal"
    trigger = "battle_end"
    amount = 1

    async def apply(self, target) -> None:
        await target.apply_healing(self.amount)
