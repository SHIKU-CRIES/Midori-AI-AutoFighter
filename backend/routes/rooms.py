from __future__ import annotations

import asyncio
import copy

from game import _run_battle
from game import battle_snapshots
from game import battle_tasks
from game import get_save_manager
from game import load_map
from game import load_party
from game import save_map
from game import save_party
from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.party import Party
from autofighter.rooms import BattleRoom
from autofighter.rooms import BossRoom
from autofighter.rooms import ChatRoom
from autofighter.rooms import RestRoom
from autofighter.rooms import ShopRoom
from autofighter.rooms import _build_foes
from autofighter.rooms import _scale_stats
from autofighter.rooms import _serialize
from plugins.damage_types import load_damage_type
from battle_logging import get_current_run_logger, start_run_logging

bp = Blueprint("rooms", __name__)


@bp.post("/rooms/<run_id>/battle")
async def battle_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    action = data.get("action", "")
    if action == "snapshot":
        snap = battle_snapshots.get(run_id)
        if snap is None:
            return jsonify({"error": "no battle"}), 404
        return jsonify(snap)
    party = await asyncio.to_thread(load_party, run_id)
    try:
        with get_save_manager().connection() as conn:
            row = conn.execute(
                "SELECT type FROM damage_types WHERE id = ?", ("player",)
            ).fetchone()
        if row and row[0]:
            for m in party.members:
                if m.id == "player":
                    m.damage_type = load_damage_type(row[0])
                    break
    except Exception:
        pass
    state, rooms = await asyncio.to_thread(load_map, run_id)
    # Ensure run logging is initialized for this run (survives server restarts)
    try:
        logger = get_current_run_logger()
        if logger is None or getattr(logger, 'run_id', None) != run_id:
            start_run_logging(run_id)
    except Exception:
        pass
    if not rooms or not (0 <= int(state.get("current", 0)) < len(rooms)):
        snap = battle_snapshots.get(run_id)
        if snap is not None:
            return jsonify(snap)
        return jsonify({"error": "run ended or room out of range"}), 404
    node = rooms[state["current"]]
    if node.room_type not in {"battle-weak", "battle-normal"}:
        return jsonify({"error": "invalid room"}), 400
    if state.get("awaiting_next"):
        return jsonify({"error": "awaiting next"}), 400
    if state.get("awaiting_card") or state.get("awaiting_relic"):
        snap = battle_snapshots.get(run_id)
        if snap is not None:
            return jsonify(snap)
        party_data = [_serialize(m) for m in party.members]
        return jsonify(
            {
                "result": "battle",
                "party": party_data,
                "foes": [],
                "gold": party.gold,
                "relics": party.relics,
                "cards": party.cards,
                "card_choices": [],
                "relic_choices": [],
                "enrage": {"active": False, "stacks": 0},
                "rdr": party.rdr,
            }
        )
    if run_id in battle_tasks:
        snap = battle_snapshots.get(run_id, {"result": "battle"})
        return jsonify(snap)
    state["battle"] = True
    await asyncio.to_thread(save_map, run_id, state)
    room = BattleRoom(node)
    foes = _build_foes(node, party)
    for f in foes:
        _scale_stats(f, node, room.strength)
    combat_party = Party(
        members=[copy.deepcopy(m) for m in party.members],
        gold=party.gold,
        relics=party.relics,
        cards=party.cards,
        rdr=party.rdr,
    )
    battle_snapshots[run_id] = {
        "result": "battle",
        "party": [_serialize(m) for m in combat_party.members],
        "foes": [_serialize(f) for f in foes],
        "gold": party.gold,
        "relics": party.relics,
        "cards": party.cards,
        "card_choices": [],
        "relic_choices": [],
        "enrage": {"active": False, "stacks": 0},
        "rdr": party.rdr,
    }
    state["battle"] = False
    await asyncio.to_thread(save_map, run_id, state)

    async def progress(snapshot: dict[str, dict | list]) -> None:
        battle_snapshots[run_id] = snapshot

    task = asyncio.create_task(
        _run_battle(run_id, room, foes, party, data, state, rooms, progress)
    )
    battle_tasks[run_id] = task
    return jsonify(battle_snapshots[run_id])


@bp.post("/rooms/<run_id>/shop")
async def shop_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    state, rooms = await asyncio.to_thread(load_map, run_id)
    # Guard against empty or out-of-range room indices (e.g., after end-of-run)
    if not rooms or not (0 <= int(state.get("current", 0)) < len(rooms)):
        snap = battle_snapshots.get(run_id)
        if snap is not None:
            return jsonify(snap)
        return jsonify({"error": "run ended or room out of range"}), 404
    node = rooms[state["current"]]
    if node.room_type != "shop":
        return jsonify({"error": "invalid room"}), 400
    stock_state = state.setdefault("shop_stock", {})
    node_stock = stock_state.get(str(node.room_id))
    if node_stock is not None:
        setattr(node, "stock", node_stock)
    room = ShopRoom(node)
    party = await asyncio.to_thread(load_party, run_id)
    # resolve is async; must await to get the result dict
    result = await room.resolve(party, data)
    stock_state[str(node.room_id)] = getattr(node, "stock", [])
    state["shop_stock"] = stock_state
    action = data.get("action", "")
    next_type = None
    if action == "leave":
        state["awaiting_next"] = True
        next_type = (
            rooms[state["current"] + 1].room_type
            if state["current"] + 1 < len(rooms)
            else None
        )
    else:
        state["awaiting_next"] = False
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    payload = {**result}
    if next_type is not None:
        payload["next_room"] = next_type
    return jsonify(payload)


@bp.post("/rooms/<run_id>/rest")
async def rest_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    state, rooms = await asyncio.to_thread(load_map, run_id)
    node = rooms[state["current"]]
    if node.room_type != "rest":
        return jsonify({"error": "invalid room"}), 400
    room = RestRoom(node)
    party = await asyncio.to_thread(load_party, run_id)
    # resolve is async; must await to get the result dict
    result = await room.resolve(party, data)
    # Mark room as completable and expose the next room type for the UI
    state["awaiting_next"] = True
    next_type = (
        rooms[state["current"] + 1].room_type
        if state["current"] + 1 < len(rooms)
        else None
    )
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    return jsonify({**result, "next_room": next_type})


@bp.post("/rooms/<run_id>/chat")
async def chat_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    state, rooms = await asyncio.to_thread(load_map, run_id)
    node = rooms[state["current"]]
    if node.room_type != "chat":
        return jsonify({"error": "invalid room"}), 400
    room = ChatRoom(node)
    party = await asyncio.to_thread(load_party, run_id)
    result = await room.resolve(party, data)
    # Chat rooms should also be leaveable
    state["awaiting_next"] = True
    next_type = (
        rooms[state["current"] + 1].room_type
        if state["current"] + 1 < len(rooms)
        else None
    )
    await asyncio.to_thread(save_map, run_id, state)
    await asyncio.to_thread(save_party, run_id, party)
    return jsonify({**result, "next_room": next_type})


@bp.post("/rooms/<run_id>/boss")
async def boss_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    # Support polling snapshots via the boss endpoint too
    action = data.get("action", "")
    if action == "snapshot":
        snap = battle_snapshots.get(run_id)
        if snap is None:
            return jsonify({"error": "no battle"}), 404
        return jsonify(snap)

    state, rooms = await asyncio.to_thread(load_map, run_id)
    # Ensure run logging is initialized for this run
    try:
        logger = get_current_run_logger()
        if logger is None or getattr(logger, 'run_id', None) != run_id:
            start_run_logging(run_id)
    except Exception:
        pass
    node = rooms[state["current"]]
    if node.room_type != "battle-boss-floor":
        return jsonify({"error": "invalid room"}), 400
    if state.get("awaiting_next"):
        return jsonify({"error": "awaiting next"}), 400
    if state.get("awaiting_card") or state.get("awaiting_relic"):
        snap = battle_snapshots.get(run_id)
        if snap is not None:
            return jsonify(snap)
        party = await asyncio.to_thread(load_party, run_id)
        party_data = [_serialize(m) for m in party.members]
        return jsonify(
            {
                "result": "boss",
                "party": party_data,
                "foes": [],
                "gold": party.gold,
                "relics": party.relics,
                "cards": party.cards,
                "card_choices": [],
                "relic_choices": [],
                "enrage": {"active": False, "stacks": 0},
            }
        )

    # Mirror battle flow: prime snapshot, then resolve in background task
    state["battle"] = True
    await asyncio.to_thread(save_map, run_id, state)
    room = BossRoom(node)
    party = await asyncio.to_thread(load_party, run_id)
    foes = _build_foes(node, party)
    for f in foes:
        _scale_stats(f, node, room.strength)
    combat_party = Party(
        members=[copy.deepcopy(m) for m in party.members],
        gold=party.gold,
        relics=party.relics,
        cards=party.cards,
        rdr=party.rdr,
    )
    battle_snapshots[run_id] = {
        "result": "boss",
        "party": [_serialize(m) for m in combat_party.members],
        "foes": [_serialize(f) for f in foes],
        "gold": party.gold,
        "relics": party.relics,
        "cards": party.cards,
        "card_choices": [],
        "relic_choices": [],
        "enrage": {"active": False, "stacks": 0},
        "rdr": party.rdr,
    }
    state["battle"] = False
    await asyncio.to_thread(save_map, run_id, state)

    async def progress(snapshot: dict[str, dict | list]) -> None:
        battle_snapshots[run_id] = snapshot

    task = asyncio.create_task(
        _run_battle(run_id, room, foes, party, data, state, rooms, progress)
    )
    battle_tasks[run_id] = task
    return jsonify(battle_snapshots[run_id])


@bp.post("/rooms/<run_id>/<room_id>/action")
async def room_action(run_id: str, room_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify(
        {"run_id": run_id, "room_id": room_id, "action": data.get("action", "noop")}
    )
