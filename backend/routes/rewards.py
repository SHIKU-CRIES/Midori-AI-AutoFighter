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

    # Update progression state
    progression = state.get("reward_progression")
    if progression and progression.get("current_step") == "card":
        progression["completed"].append("card")

        # Find next step in progression
        available = progression.get("available", [])
        completed = progression.get("completed", [])
        next_steps = [step for step in available if step not in completed]

        if next_steps:
            progression["current_step"] = next_steps[0]
            state["awaiting_card"] = False
            state["awaiting_next"] = False
        else:
            # All progression steps completed
            progression["current_step"] = None
            state["awaiting_card"] = False
            state["awaiting_next"] = True
            del state["reward_progression"]
    else:
        # Legacy logic for backward compatibility
        state["awaiting_card"] = False
        if not state.get("awaiting_relic") and not state.get("awaiting_loot"):
            state["awaiting_next"] = True

    next_type = (
        rooms[state["current"] + 1].room_type
        if state["current"] + 1 < len(rooms) and state.get("awaiting_next")
        else None
    )
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

    # Update progression state
    progression = state.get("reward_progression")
    if progression and progression.get("current_step") == "relic":
        progression["completed"].append("relic")

        # Find next step in progression
        available = progression.get("available", [])
        completed = progression.get("completed", [])
        next_steps = [step for step in available if step not in completed]

        if next_steps:
            progression["current_step"] = next_steps[0]
            state["awaiting_relic"] = False
            state["awaiting_next"] = False
        else:
            # All progression steps completed
            progression["current_step"] = None
            state["awaiting_relic"] = False
            state["awaiting_next"] = True
            del state["reward_progression"]
    else:
        # Legacy logic for backward compatibility
        state["awaiting_relic"] = False
        if not state.get("awaiting_card") and not state.get("awaiting_loot"):
            state["awaiting_next"] = True

    next_type = (
        rooms[state["current"] + 1].room_type
        if state["current"] + 1 < len(rooms) and state.get("awaiting_next")
        else None
    )
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    relic_data = {"id": relic.id, "name": relic.name, "stars": relic.stars}
    return jsonify({"relic": relic_data, "relics": party.relics, "next_room": next_type})


@bp.post("/loot/<run_id>")
async def acknowledge_loot(run_id: str) -> tuple[str, int, dict[str, str]]:
    """Endpoint for acknowledging loot and allowing room advancement"""
    state, rooms = await asyncio.to_thread(load_map, run_id)
    if not state.get("awaiting_loot"):
        return jsonify({"error": "not awaiting loot"}), 400

    # Update progression state
    progression = state.get("reward_progression")
    if progression and progression.get("current_step") == "loot":
        progression["completed"].append("loot")

        # Find next step in progression
        available = progression.get("available", [])
        completed = progression.get("completed", [])
        next_steps = [step for step in available if step not in completed]

        if next_steps:
            progression["current_step"] = next_steps[0]
            state["awaiting_loot"] = False
            state["awaiting_next"] = False
        else:
            # All progression steps completed
            progression["current_step"] = None
            state["awaiting_loot"] = False
            state["awaiting_next"] = True
            del state["reward_progression"]
    else:
        # Legacy logic for backward compatibility
        state["awaiting_loot"] = False
        if not state.get("awaiting_card") and not state.get("awaiting_relic"):
            state["awaiting_next"] = True

    next_type = (
        rooms[state["current"] + 1].room_type
        if state["current"] + 1 < len(rooms) and state.get("awaiting_next")
        else None
    )

    await asyncio.to_thread(save_map, run_id, state)
    return jsonify({"acknowledged": True, "next_room": next_type})
