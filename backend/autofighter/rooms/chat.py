from __future__ import annotations

import json

from dataclasses import dataclass
from typing import Any

from . import Room
from .utils import _serialize
from options import get_option
from ..party import Party
from ..passives import PassiveRegistry
from llms.loader import ModelName
from llms.loader import load_llm


@dataclass
class ChatRoom(Room):
    """Chat rooms forward a single message to an LLM character."""

    async def resolve(self, party: Party, data: dict[str, Any]) -> dict[str, Any]:
        registry = PassiveRegistry()
        for member in party.members:
            await registry.trigger("room_enter", member)
        message = data.get("message", "")
        party_data = [_serialize(p) for p in party.members]
        model = get_option("lrm_model", ModelName.DEEPSEEK.value)
        llm = load_llm(model)
        payload = {"party": party_data, "message": message}
        prompt = json.dumps(payload)
        reply = ""
        async for chunk in llm.generate_stream(prompt):
            reply += chunk
        return {
            "result": "chat",
            "message": message,
            "response": reply,
            "party": party_data,
            "gold": party.gold,
            "relics": party.relics,
            "cards": party.cards,
            "rdr": party.rdr,
            "card": None,
            "foes": [],
        }
