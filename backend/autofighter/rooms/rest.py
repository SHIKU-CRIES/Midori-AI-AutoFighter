from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..party import Party
from ..passives import PassiveRegistry
from . import Room
from .utils import _serialize


@dataclass
class RestRoom(Room):
    """Rest rooms fully heal the party without combat."""

    async def resolve(self, party: Party, data: dict[str, Any]) -> dict[str, Any]:
        registry = PassiveRegistry()
        for member in party.members:
            await registry.trigger("room_enter", member)
            await member.apply_healing(member.max_hp)
        party_data = [_serialize(p) for p in party.members]
        return {
            "result": "rest",
            "party": party_data,
            "gold": party.gold,
            "relics": party.relics,
            "cards": party.cards,
            "rdr": party.rdr,
            "card": None,
            "foes": [],
        }
