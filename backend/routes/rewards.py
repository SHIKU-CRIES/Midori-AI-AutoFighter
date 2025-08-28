from __future__ import annotations

import asyncio

from game import load_map
from game import load_party
from game import save_map
from game import save_party
from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.cards import award_card
from autofighter.relics import award_relic

bp = Blueprint("rewards", __name__)


@bp.post("/cards/<run_id>")
async def select_card(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    card_id = data.get("card")
    if not card_id:
        return jsonify({"error": "invalid card"}), 400
    party = await asyncio.to_thread(load_party, run_id)
    card = award_card(party, card_id)
    if card is None:
        return jsonify({"error": "invalid card"}), 400
    state, rooms = await asyncio.to_thread(load_map, run_id)
    state["awaiting_card"] = False
    if not state.get("awaiting_relic"):
        state["awaiting_next"] = True
        next_type = (
            rooms[state["current"] + 1].room_type
            if state["current"] + 1 < len(rooms)
            else None
        )
    else:
        state["awaiting_next"] = False
        next_type = None
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    card_data = {"id": card.id, "name": card.name, "stars": card.stars}
    return jsonify({"card": card_data, "cards": party.cards, "next_room": next_type})


@bp.post("/relics/<run_id>")
async def select_relic(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    relic_id = data.get("relic")
    if not relic_id:
        return jsonify({"error": "invalid relic"}), 400
    party = await asyncio.to_thread(load_party, run_id)
    relic = award_relic(party, relic_id)
    if relic is None:
        return jsonify({"error": "invalid relic"}), 400
    state, rooms = await asyncio.to_thread(load_map, run_id)
    state["awaiting_relic"] = False
    if not state.get("awaiting_card"):
        state["awaiting_next"] = True
        next_type = (
            rooms[state["current"] + 1].room_type
            if state["current"] + 1 < len(rooms)
            else None
        )
    else:
        state["awaiting_next"] = False
        next_type = None
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    relic_data = {"id": relic.id, "name": relic.name, "stars": relic.stars}
    return jsonify({"relic": relic_data, "relics": party.relics, "next_room": next_type})
