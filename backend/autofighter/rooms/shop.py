from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..party import Party
from ..passives import PassiveRegistry
from . import Room
from .utils import _serialize


@dataclass
class ShopRoom(Room):
    """Shop rooms allow relic purchases and heal the party slightly."""

    async def resolve(self, party: Party, data: dict[str, Any]) -> dict[str, Any]:
        registry = PassiveRegistry()
        heal = int(sum(m.max_hp for m in party.members) * 0.05)
        for member in party.members:
            await registry.trigger("room_enter", member)
            await member.apply_healing(heal)
        cost = int(data.get("cost", 0))
        item = data.get("item")
        if cost > 0 and party.gold >= cost:
            party.gold -= cost
            if item:
                party.relics.append(item)
        party_data = [_serialize(p) for p in party.members]
        return {
            "result": "shop",
            "party": party_data,
            "gold": party.gold,
            "relics": party.relics,
            "cards": party.cards,
            "rdr": party.rdr,
            "card": None,
            "foes": [],
        }
