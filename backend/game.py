from __future__ import annotations

import json
import base64
import random
import asyncio
import hashlib
import logging

from typing import Any
from typing import Callable
from typing import Awaitable
from pathlib import Path

from cryptography.fernet import Fernet

from plugins import passives as passive_plugins
from plugins import players as player_plugins
from plugins.damage_types import load_damage_type
from plugins.players._base import PlayerBase

from autofighter.gacha import GachaManager
from autofighter.mapgen import MapNode
from autofighter.party import Party
from autofighter.rooms import BattleRoom
from autofighter.rooms import _build_foes  # noqa: F401
from autofighter.rooms import _scale_stats  # noqa: F401
from autofighter.rooms import _serialize  # noqa: F401
from autofighter.save_manager import SaveManager
from autofighter.stats import Stats

log = logging.getLogger(__name__)

SAVE_MANAGER = SaveManager.from_env()
SAVE_MANAGER.migrate(Path(__file__).resolve().parent / "migrations")
with SAVE_MANAGER.connection() as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS damage_types (id TEXT PRIMARY KEY, type TEXT)"
    )
    count = conn.execute("SELECT COUNT(*) FROM owned_players").fetchone()[0]
    if count == 1:
        persona = random.choice(["lady_darkness", "lady_light"])
        conn.execute("INSERT INTO owned_players (id) VALUES (?)", (persona,))

FERNET_KEY = base64.urlsafe_b64encode(
    hashlib.sha256((SAVE_MANAGER.key or "plaintext").encode()).digest()
)
FERNET = Fernet(FERNET_KEY)

battle_tasks: dict[str, asyncio.Task] = {}
battle_snapshots: dict[str, dict[str, Any]] = {}

def _passive_names(ids: list[str]) -> list[str]:
    names: list[str] = []
    for pid in ids:
        for mod in passive_plugins.__all__:
            cls = getattr(passive_plugins, mod)
            if getattr(cls, "id", None) == pid:
                names.append(getattr(cls, "name", pid))
                break
    return names

def _load_player_customization() -> tuple[str, dict[str, int]]:
    pronouns = ""
    stats: dict[str, int] = {"hp": 0, "attack": 0, "defense": 0}
    with SAVE_MANAGER.connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
        )
        cur = conn.execute(
            "SELECT value FROM options WHERE key = ?", ("player_pronouns",)
        )
        row = cur.fetchone()
        if row:
            pronouns = row[0]
        cur = conn.execute("SELECT value FROM options WHERE key = ?", ("player_stats",))
        row = cur.fetchone()
        if row:
            try:
                stats.update(json.loads(row[0]))
            except (TypeError, ValueError, json.JSONDecodeError):
                pass
    return pronouns, stats

def _apply_player_stats(
    player: PlayerBase,
    stats: dict[str, int] | None = None,
) -> None:
    _, loaded = _load_player_customization()
    if stats is None:
        stats = loaded
    hp_mod = 1 + stats.get("hp", 0) * 0.01
    atk_mod = 1 + stats.get("attack", 0) * 0.01
    def_mod = 1 + stats.get("defense", 0) * 0.01
    player.max_hp = player.hp = int(player.hp * hp_mod)
    player.atk = int(player.atk * atk_mod)
    player.defense = int(player.defense * def_mod)

def _assign_damage_type(player: PlayerBase) -> None:
    with SAVE_MANAGER.connection() as conn:
        cur = conn.execute("SELECT type FROM damage_types WHERE id = ?", (player.id,))
        row = cur.fetchone()
        if row:
            player.damage_type = load_damage_type(row[0])
        else:
            conn.execute(
                "INSERT INTO damage_types (id, type) VALUES (?, ?)",
                (player.id, player.element_id),
            )

def load_party(run_id: str) -> Party:
    with SAVE_MANAGER.connection() as conn:
        cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
        row = cur.fetchone()
    data = json.loads(row[0]) if row else {}
    if isinstance(data, list):
        data = {"members": data, "gold": 0, "relics": [], "cards": []}
    snapshot = data.get("player", {})
    exp_map: dict[str, int] = data.get("exp", {})
    level_map: dict[str, int] = data.get("level", {})
    exp_mult_map: dict[str, float] = data.get("exp_multiplier", {})
    members: list[PlayerBase] = []
    for pid in data.get("members", []):
        for name in player_plugins.__all__:
            cls = getattr(player_plugins, name)
            if cls.id == pid:
                inst = cls()
                if inst.id == "player":
                    with SAVE_MANAGER.connection() as conn:
                        row = conn.execute(
                            "SELECT type FROM damage_types WHERE id = ?", ("player",)
                        ).fetchone()
                    if row and row[0]:
                        inst.damage_type = load_damage_type(row[0])
                    else:
                        inst.damage_type = load_damage_type(
                            snapshot.get("damage_type", inst.element_id)
                        )
                    _apply_player_stats(inst, snapshot.get("stats", {}))
                else:
                    _assign_damage_type(inst)
                target_level = int(level_map.get(pid, 1) or 1)
                if target_level > 1:
                    for _ in range(target_level - 1):
                        inst._on_level_up()
                inst.level = target_level
                inst.exp = int(exp_map.get(pid, 0) or 0)
                try:
                    inst.exp_multiplier = float(
                        exp_mult_map.get(pid, inst.exp_multiplier)
                    )
                except Exception:
                    pass
                members.append(inst)
                break
    party = Party(
        members=members,
        gold=data.get("gold", 0),
        relics=data.get("relics", []),
        cards=data.get("cards", []),
        rdr=data.get("rdr", 1.0),
    )
    return party

def load_map(run_id: str) -> tuple[dict, list[MapNode]]:
    with SAVE_MANAGER.connection() as conn:
        cur = conn.execute("SELECT map FROM runs WHERE id = ?", (run_id,))
        row = cur.fetchone()
    if row is None:
        return {"rooms": [], "current": 0, "battle": False}, []
    state = json.loads(row[0])
    rooms = [MapNode.from_dict(n) for n in state.get("rooms", [])]
    return state, rooms

def save_map(run_id: str, state: dict) -> None:
    with SAVE_MANAGER.connection() as conn:
        conn.execute(
            "UPDATE runs SET map = ? WHERE id = ?",
            (json.dumps(state), run_id),
        )

def save_party(run_id: str, party: Party) -> None:
    with SAVE_MANAGER.connection() as conn:
        cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
        row = cur.fetchone()
    existing = json.loads(row[0]) if row else {}
    snapshot = existing.get("player", {})
    for member in party.members:
        if member.id == "player":
            base = player_plugins.player.Player()
            stats = {
                "hp": int(round((member.max_hp / base.max_hp - 1) * 100)),
                "attack": int(round((member.atk / base.atk - 1) * 100)),
                "defense": int(round((member.defense / base.defense - 1) * 100)),
            }
            snapshot = {
                **snapshot,
                "damage_type": member.element_id,
                "stats": stats,
            }
            break
    with SAVE_MANAGER.connection() as conn:
        data = {
            "members": [m.id for m in party.members],
            "gold": party.gold,
            "relics": party.relics,
            "cards": party.cards,
            "exp": {m.id: m.exp for m in party.members},
            "level": {m.id: m.level for m in party.members},
            "exp_multiplier": {m.id: m.exp_multiplier for m in party.members},
            "rdr": party.rdr,
            "player": snapshot,
        }
        conn.execute(
            "UPDATE runs SET party = ? WHERE id = ?",
            (json.dumps(data), run_id),
        )

async def _run_battle(
    run_id: str,
    room: BattleRoom,
    foes: Stats | list[Stats],
    party: Party,
    data: dict[str, Any],
    state: dict[str, Any],
    rooms: list[MapNode],
    progress: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    try:
        try:
            result = await room.resolve(party, data, progress, foes)
        except Exception as exc:
            state["battle"] = False
            log.exception("Battle resolution failed for %s", run_id)
            battle_snapshots[run_id] = {
                "result": "error",
                "error": str(exc),
                "ended": True,
                "party": [],
                "foes": [],
                "awaiting_next": False,
            }
            try:
                await asyncio.to_thread(save_map, run_id, state)
                await asyncio.to_thread(save_party, run_id, party)
            except Exception:
                pass
            return
        state["battle"] = False
        try:
            loot_items = result.get("loot", {}).get("items", [])
            manager = GachaManager(SAVE_MANAGER)
            items = manager._get_items()
            for entry in loot_items:
                if entry.get("id") == "ticket":
                    items["ticket"] = items.get("ticket", 0) + 1
                else:
                    key = f"{entry['id']}_{entry['stars']}"
                    items[key] = items.get(key, 0) + 1
            if manager._get_auto_craft():
                manager._auto_craft(items)
            manager._set_items(items)
            result["items"] = items
            if result.get("result") == "defeat":
                state["awaiting_card"] = False
                state["awaiting_relic"] = False
                state["awaiting_next"] = False
                try:
                    await asyncio.to_thread(save_map, run_id, state)
                    await asyncio.to_thread(save_party, run_id, party)
                    result.update(
                        {
                            "run_id": run_id,
                            "current_room": rooms[state["current"]].room_type,
                            "current_index": state["current"],
                            "awaiting_card": False,
                            "awaiting_relic": False,
                            "awaiting_next": False,
                            "next_room": None,
                            "ended": True,
                        }
                    )
                    battle_snapshots[run_id] = result
                finally:
                    try:
                        with SAVE_MANAGER.connection() as conn:
                            conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
                    except Exception:
                        pass
                return
            has_card_choices = bool(result.get("card_choices"))
            has_relic_choices = bool(result.get("relic_choices"))
            if has_card_choices or has_relic_choices:
                state["awaiting_card"] = has_card_choices
                state["awaiting_relic"] = has_relic_choices
                state["awaiting_next"] = False
                next_type = None
            else:
                state["awaiting_next"] = True
                next_type = (
                    rooms[state["current"] + 1].room_type
                    if state["current"] + 1 < len(rooms)
                    else None
                )
            await asyncio.to_thread(save_map, run_id, state)
            await asyncio.to_thread(save_party, run_id, party)
            result.update(
                {
                    "run_id": run_id,
                    "action": data.get("action", ""),
                    "next_room": next_type,
                    "current_room": rooms[state["current"]].room_type,
                    "current_index": state["current"],
                    "awaiting_card": state.get("awaiting_card", False),
                    "awaiting_relic": state.get("awaiting_relic", False),
                    "awaiting_next": state.get("awaiting_next", False),
                }
            )
            battle_snapshots[run_id] = result
        except Exception as exc:
            log.exception("Battle processing failed for %s", run_id)
            battle_snapshots[run_id] = {
                "result": "error",
                "loot": result.get("loot"),
                "error": str(exc),
                "ended": True,
                "party": [],
                "foes": [],
                "awaiting_next": False,
            }
    finally:
        battle_tasks.pop(run_id, None)
