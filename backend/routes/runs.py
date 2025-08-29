from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
import random
from uuid import uuid4

from battle_logging import end_run_logging

# Import battle logging
from battle_logging import start_run_logging
from game import _assign_damage_type
from game import _load_player_customization
from game import _passive_names
from game import battle_snapshots
from game import battle_tasks
from game import get_fernet
from game import get_save_manager
from game import load_map
from game import save_map
from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.mapgen import MapGenerator
from plugins import players as player_plugins

bp = Blueprint("runs", __name__)


@bp.post("/run/start")
async def start_run() -> tuple[str, int, dict[str, object]]:
    data = await request.get_json(silent=True) or {}
    members: list[str] = data.get("party", [])
    damage_type = (data.get("damage_type") or "").capitalize()
    if (
        "player" not in members
        or not 1 <= len(members) <= 5
        or len(set(members)) != len(members)
    ):
        return jsonify({"error": "invalid party"}), 400

    def get_owned_players():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT id FROM owned_players")
            return {row[0] for row in cur.fetchall()}

    owned = await asyncio.to_thread(get_owned_players)
    for mid in members:
        if mid != "player" and mid not in owned:
            return jsonify({"error": "unowned character"}), 400
    if damage_type:
        allowed = {"Light", "Dark", "Wind", "Lightning", "Fire", "Ice"}
        if damage_type not in allowed:
            return jsonify({"error": "invalid damage type"}), 400

        def set_damage_type():
            with get_save_manager().connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO damage_types (id, type) VALUES (?, ?)",
                    ("player", damage_type),
                )

        await asyncio.to_thread(set_damage_type)
    run_id = str(uuid4())

    # Start run logging
    start_run_logging(run_id)

    generator = MapGenerator(run_id)
    nodes = generator.generate_floor()
    state = {
        "rooms": [n.to_dict() for n in nodes],
        "current": 1,
        "battle": False,
        "awaiting_card": False,
        "awaiting_relic": False,
        "awaiting_next": False,
    }
    pronouns, stats = await asyncio.to_thread(_load_player_customization)

    def get_player_damage_type():
        with get_save_manager().connection() as conn:
            cur = conn.execute(
                "SELECT type FROM damage_types WHERE id = ?",
                ("player",),
            )
            return cur.fetchone()

    row = await asyncio.to_thread(get_player_damage_type)
    player_type = row[0] if row else player_plugins.player.Player().element_id
    snapshot = {
        "pronouns": pronouns,
        "damage_type": player_type,
        "stats": stats,
    }

    def save_new_run():
        with get_save_manager().connection() as conn:
            conn.execute(
                "INSERT INTO runs (id, party, map) VALUES (?, ?, ?)",
                (
                    run_id,
                    json.dumps(
                        {
                            "members": members,
                            "gold": 0,
                            "relics": [],
                            "cards": [],
                            "exp": dict.fromkeys(members, 0),
                            "level": dict.fromkeys(members, 1),
                            "rdr": 1.0,
                            "player": snapshot,
                        }
                    ),
                    json.dumps(state),
                ),
            )

    await asyncio.to_thread(save_new_run)
    party_info: list[dict[str, object]] = []
    for pid in members:
        for name in player_plugins.__all__:
            cls = getattr(player_plugins, name)
            if cls.id == pid:
                inst = cls()
                inst.exp = 0
                inst.level = 1
                _assign_damage_type(inst)
                party_info.append(
                    {
                        "id": inst.id,
                        "name": inst.name,
                        "passives": _passive_names(getattr(inst, "passives", [])),
                        "exp": inst.exp,
                        "level": inst.level,
                    }
                )
                break
    return jsonify({"run_id": run_id, "map": state, "party": party_info})


@bp.put("/party/<run_id>")
async def update_party(run_id: str) -> tuple[str, int, dict[str, object]]:
    data = await request.get_json(silent=True) or {}
    members = data.get("party", [])
    gold = data.get("gold", 0)
    relics = data.get("relics", [])
    cards = data.get("cards", [])
    rdr = data.get("rdr", 1.0)
    if (
        "player" not in members
        or not 1 <= len(members) <= 5
        or len(set(members)) != len(members)
    ):
        return jsonify({"error": "invalid party"}), 400

    def get_owned_players():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT id FROM owned_players")
            return {row[0] for row in cur.fetchall()}

    owned = await asyncio.to_thread(get_owned_players)
    for mid in members:
        if mid != "player" and mid not in owned:
            return jsonify({"error": "unowned character"}), 400
    party = {
        "members": members,
        "gold": gold,
        "relics": relics,
        "cards": cards,
        "exp": dict.fromkeys(members, 0),
        "level": dict.fromkeys(members, 1),
        "rdr": rdr,
    }

    def update_party_data():
        with get_save_manager().connection() as conn:
            conn.execute(
                "UPDATE runs SET party = ? WHERE id = ?",
                (json.dumps(party), run_id),
            )

    await asyncio.to_thread(update_party_data)
    return jsonify({"party": members})


@bp.get("/map/<run_id>")
async def get_map(run_id: str) -> tuple[str, int, dict[str, object]]:
    # Ensure run logging is initialized for this run (handles server restarts)
    try:
        from battle_logging import get_current_run_logger, start_run_logging  # local import to avoid cycles
        logger = get_current_run_logger()
        if logger is None or getattr(logger, 'run_id', None) != run_id:
            start_run_logging(run_id)
    except Exception:
        pass
    def get_run_data():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT map, party FROM runs WHERE id = ?", (run_id,))
            return cur.fetchone()

    row = await asyncio.to_thread(get_run_data)
    if row is None:
        return jsonify({"error": "run not found"}), 404
    map_state = json.loads(row[0])
    party_state = json.loads(row[1]) if row[1] else {}
    return jsonify({"map": map_state, "party": party_state.get("members", [])})


@bp.delete("/run/<run_id>")
async def end_run(run_id: str) -> tuple[str, int, dict[str, str]]:
    task = battle_tasks.pop(run_id, None)
    try:
        if task is not None and not task.done():
            task.cancel()
            try:
                await asyncio.sleep(0.001)
            except Exception:
                pass
    except Exception:
        pass
    battle_snapshots.pop(run_id, None)

    def delete_run():
        with get_save_manager().connection() as conn:
            cur = conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
            return cur.rowcount

    # End run logging before deleting
    end_run_logging()

    rowcount = await asyncio.to_thread(delete_run)
    if rowcount == 0:
        return jsonify({"error": "run not found"}), 404
    return jsonify({"status": "ended"})


@bp.post("/run/<run_id>/next")
async def advance_room(run_id: str) -> tuple[str, int, dict[str, object]]:
    state, rooms = await asyncio.to_thread(load_map, run_id)
    if state.get("awaiting_card") or state.get("awaiting_relic"):
        return jsonify({"error": "awaiting reward"}), 400
    if not state.get("awaiting_next"):
        return jsonify({"error": "not ready"}), 400
    state["current"] += 1
    state["awaiting_next"] = False

    # If we have advanced past the end of the current floor, generate a new floor.
    if state["current"] >= len(rooms):
        try:
            last = rooms[-1]
            next_floor = int(getattr(last, "floor", 1)) + 1
            loop = int(getattr(last, "loop", 1))
            pressure = int(getattr(last, "pressure", 0))
        except Exception:
            next_floor, loop, pressure = 1, 1, 0

        # Generate the next floor using a seed derived from run_id and floor
        generator = MapGenerator(f"{run_id}-floor-{next_floor}", floor=next_floor, loop=loop, pressure=pressure)
        nodes = generator.generate_floor()
        state["rooms"] = [n.to_dict() for n in nodes]
        state["current"] = 1  # enter at room index 1 (after start)
        next_type = nodes[state["current"]].room_type if state["current"] < len(nodes) else None
    else:
        # Continue within the current floor
        next_type = rooms[state["current"]].room_type if state["current"] < len(rooms) else None

    await asyncio.to_thread(save_map, run_id, state)
    return jsonify({"next_room": next_type, "current_index": state["current"]})


@bp.get("/run/<run_id>/battles/<int:index>/summary")
async def get_battle_summary(run_id: str, index: int):
    summary_path = (
        Path(__file__).resolve().parents[1]
        / "logs"
        / "runs"
        / run_id
        / "battles"
        / str(index)
        / "summary"
        / "battle_summary.json"
    )
    if not summary_path.exists():
        return jsonify({"error": "summary not found"}), 404

    data = await asyncio.to_thread(summary_path.read_text)
    return jsonify(json.loads(data))


@bp.get("/run/<run_id>/battles/<int:index>/events")
async def get_battle_events(run_id: str, index: int):
    events_path = (
        Path(__file__).resolve().parents[1]
        / "logs"
        / "runs"
        / run_id
        / "battles"
        / str(index)
        / "summary"
        / "events.json"
    )
    if not events_path.exists():
        return jsonify({"error": "events not found"}), 404

    data = await asyncio.to_thread(events_path.read_text)
    return jsonify(json.loads(data))


@bp.post("/save/wipe")
async def wipe_save() -> tuple[str, int, dict[str, str]]:
    def do_wipe():
        manager = get_save_manager()
        manager.db_path.unlink(missing_ok=True)
        manager.migrate(Path(__file__).resolve().parent / "migrations")
        persona = random.choice(["lady_darkness", "lady_light"])
        with manager.connection() as conn:
            conn.execute("INSERT INTO owned_players (id) VALUES (?)", (persona,))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS damage_types (id TEXT PRIMARY KEY, type TEXT)"
            )

    await asyncio.to_thread(do_wipe)
    return jsonify({"status": "wiped"})


@bp.get("/save/backup")
async def backup_save() -> tuple[bytes, int, dict[str, str]]:
    def get_backup_data():
        with get_save_manager().connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS damage_types (id TEXT PRIMARY KEY, type TEXT)"
            )
            runs = conn.execute("SELECT id, party, map FROM runs").fetchall()
            options = conn.execute("SELECT key, value FROM options").fetchall()
            dmg = conn.execute("SELECT id, type FROM damage_types").fetchall()
        return {"runs": runs, "options": options, "damage_types": dmg}

    payload = await asyncio.to_thread(get_backup_data)
    data = json.dumps(payload)
    digest = hashlib.sha256(data.encode()).hexdigest()
    package = json.dumps({"hash": digest, "data": data}).encode()
    token = get_fernet().encrypt(package)
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": "attachment; filename=backup.afsave",
    }
    return token, 200, headers


@bp.post("/save/restore")
async def restore_save() -> tuple[str, int, dict[str, str]]:
    blob = await request.get_data()
    try:
        package = get_fernet().decrypt(blob)
        obj = json.loads(package)
    except Exception:
        return jsonify({"error": "invalid backup"}), 400
    data = obj.get("data", "")
    digest = obj.get("hash", "")
    if hashlib.sha256(data.encode()).hexdigest() != digest:
        return jsonify({"error": "hash mismatch"}), 400
    payload = json.loads(data)

    def restore_data():
        with get_save_manager().connection() as conn:
            conn.execute("DELETE FROM runs")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute("DELETE FROM options")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS damage_types (id TEXT PRIMARY KEY, type TEXT)"
            )
            conn.execute("DELETE FROM damage_types")
            conn.executemany(
                "INSERT INTO runs (id, party, map) VALUES (?, ?, ?)", payload["runs"]
            )
            conn.executemany(
                "INSERT INTO options (key, value) VALUES (?, ?)", payload["options"]
            )
            conn.executemany(
                "INSERT INTO damage_types (id, type) VALUES (?, ?)", payload["damage_types"]
            )

    await asyncio.to_thread(restore_data)
    return jsonify({"status": "restored"})
