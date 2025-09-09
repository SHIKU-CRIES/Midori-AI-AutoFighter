from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
import random
from uuid import uuid4

from battle_logging import start_run_logging
from game import _assign_damage_type
from game import _describe_passives
from game import _load_player_customization
from game import battle_snapshots
from game import battle_tasks
from game import get_fernet
from game import get_save_manager
from game import load_map
from game import save_map

from autofighter.mapgen import MapGenerator
from plugins import players as player_plugins


async def start_run(
    members: list[str],
    damage_type: str = "",
    pressure: int = 0,
) -> dict[str, object]:
    """Create a new run and return its initial state."""
    damage_type = (damage_type or "").capitalize()

    if (
        "player" not in members
        or not 1 <= len(members) <= 5
        or len(set(members)) != len(members)
    ):
        raise ValueError("invalid party")

    def get_owned_players():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT id FROM owned_players")
            return {row[0] for row in cur.fetchall()}

    owned = await asyncio.to_thread(get_owned_players)
    for mid in members:
        if mid == "mimic":
            raise ValueError("invalid party")
        if mid != "player" and mid not in owned:
            raise ValueError("unowned character")

    if damage_type:
        allowed = {"Light", "Dark", "Wind", "Lightning", "Fire", "Ice"}
        if damage_type not in allowed:
            raise ValueError("invalid damage type")

        def set_damage_type():
            with get_save_manager().connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO damage_types (id, type) VALUES (?, ?)",
                    ("player", damage_type),
                )

        await asyncio.to_thread(set_damage_type)

    run_id = str(uuid4())
    start_run_logging(run_id)

    generator = MapGenerator(run_id, pressure=pressure)
    nodes = generator.generate_floor()
    state = {
        "rooms": [n.to_dict() for n in nodes],
        "current": 1,
        "battle": False,
        "awaiting_card": False,
        "awaiting_relic": False,
        "awaiting_loot": False,
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
                        "passives": _describe_passives(inst),
                        "exp": inst.exp,
                        "level": inst.level,
                    }
                )
                break
    return {"run_id": run_id, "map": state, "party": party_info}


async def get_map(run_id: str) -> dict[str, object]:
    try:
        from battle_logging import get_current_run_logger  # local import
        logger = get_current_run_logger()
        if logger is None or getattr(logger, "run_id", None) != run_id:
            start_run_logging(run_id)
    except Exception:
        pass
    state, rooms = await asyncio.to_thread(load_map, run_id)
    if not state:
        raise ValueError("run not found")

    def get_party_data():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
            row = cur.fetchone()
            return json.loads(row[0]) if row and row[0] else {}

    party_state = await asyncio.to_thread(get_party_data)

    current_index = int(state.get("current", 0))
    current_room_data = None
    current_room_type = None
    next_room_type = None

    if rooms and 0 <= current_index < len(rooms):
        current_node = rooms[current_index]
        current_room_type = current_node.room_type
        if current_index + 1 < len(rooms):
            next_room_type = rooms[current_index + 1].room_type
        snap = battle_snapshots.get(run_id)
        if snap is not None and current_room_type in {
            "battle-weak",
            "battle-normal",
            "battle-boss-floor",
        }:
            current_room_data = snap
        elif state.get("awaiting_next"):
            result = (
                "boss"
                if current_room_type == "battle-boss-floor"
                else current_room_type.replace("-", "_") if current_room_type else "unknown"
            )
            current_room_data = {
                "result": result,
                "awaiting_next": True,
                "current_index": current_index,
                "current_room": current_room_type,
                "next_room": next_room_type,
            }

    return {
        "map": state,
        "party": party_state.get("members", []),
        "current_state": {
            "current_index": current_index,
            "current_room_type": current_room_type,
            "next_room_type": next_room_type,
            "awaiting_next": state.get("awaiting_next", False),
            "awaiting_card": state.get("awaiting_card", False),
            "awaiting_relic": state.get("awaiting_relic", False),
            "awaiting_loot": state.get("awaiting_loot", False),
            "room_data": current_room_data,
        },
    }


async def advance_room(run_id: str) -> dict[str, object]:
    state, rooms = await asyncio.to_thread(load_map, run_id)
    if not rooms:
        raise ValueError("run not found")

    if (
        state.get("awaiting_card")
        or state.get("awaiting_relic")
        or state.get("awaiting_loot")
    ):
        raise ValueError("pending rewards must be collected before advancing")

    # Reset live battle state when advancing
    battle_snapshots.pop(run_id, None)
    task = battle_tasks.pop(run_id, None)
    if task and not task.done():
        task.cancel()

    state["current"] += 1
    state["awaiting_next"] = False

    if state["current"] >= len(rooms):
        try:
            last = rooms[-1]
            next_floor = int(getattr(last, "floor", 1)) + 1
            loop = int(getattr(last, "loop", 1))
            pressure = int(getattr(last, "pressure", 0))
        except Exception:
            next_floor, loop, pressure = 1, 1, 0

        generator = MapGenerator(
            f"{run_id}-floor-{next_floor}", floor=next_floor, loop=loop, pressure=pressure
        )
        nodes = generator.generate_floor()
        state["rooms"] = [n.to_dict() for n in nodes]
        state["current"] = 1
        next_type = nodes[state["current"]].room_type if state["current"] < len(nodes) else None
    else:
        next_type = (
            rooms[state["current"]].room_type if state["current"] < len(rooms) else None
        )

    await asyncio.to_thread(save_map, run_id, state)
    return {"next_room": next_type, "current_index": state["current"]}


async def get_battle_summary(run_id: str, index: int) -> dict[str, object] | None:
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
        return None
    data = await asyncio.to_thread(summary_path.read_text)
    return json.loads(data)


async def get_battle_events(run_id: str, index: int) -> dict[str, object] | None:
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
        return None
    data = await asyncio.to_thread(events_path.read_text)
    return json.loads(data)


async def wipe_save() -> None:
    def do_wipe():
        manager = get_save_manager()
        manager.db_path.unlink(missing_ok=True)
        manager.migrate(Path(__file__).resolve().parent.parent / "migrations")
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


async def backup_save() -> bytes:
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
    return token


async def restore_save(blob: bytes) -> None:
    try:
        package = get_fernet().decrypt(blob)
        obj = json.loads(package)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("invalid backup") from exc
    data = obj.get("data", "")
    digest = obj.get("hash", "")
    if hashlib.sha256(data.encode()).hexdigest() != digest:
        raise ValueError("hash mismatch")
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
