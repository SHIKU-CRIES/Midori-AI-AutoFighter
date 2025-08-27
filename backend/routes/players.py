from __future__ import annotations

import asyncio
from dataclasses import fields
import json
import logging

from game import _apply_player_customization
from game import _assign_damage_type
from game import _load_player_customization
from game import get_save_manager
from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.stats import apply_status_hooks
from plugins import players as player_plugins

bp = Blueprint("players", __name__)
log = logging.getLogger(__name__)


def _get_stat_refresh_rate() -> int:
    def get_rate():
        with get_save_manager().connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            cur = conn.execute(
                "SELECT value FROM options WHERE key = ?", ("stat_refresh_rate",)
            )
            return cur.fetchone()

    try:
        # This function is called synchronously from sync endpoints for now
        # Could be made async in the future if needed
        row = get_rate()
        rate = int(row[0]) if row else 5
    except (TypeError, ValueError):
        rate = 5
    return max(1, min(rate, 10))


@bp.get("/players")
async def get_players() -> tuple[str, int, dict[str, str]]:
    def _serialize_stats(obj) -> dict:
        data: dict[str, object] = {}
        # Build a dict without triggering dataclasses.asdict deep-copy, which
        # chokes on complex objects (e.g., langchain/pydantic bindings).
        for f in fields(obj):
            name = f.name
            if name == "lrm_memory":
                # Non-serializable, runtime-only memory object
                continue
            value = getattr(obj, name)
            if name == "char_type":
                # Enum-like object; surface the name/string
                try:
                    data[name] = value.name
                except Exception:
                    data[name] = str(value)
                continue
            if name == "damage_type":
                # Surface damage type as element id string
                try:
                    data[name] = obj.element_id
                except Exception:
                    data[name] = str(value)
                continue
            # Keep primitives as-is, shallow-copy containers, stringify others
            if isinstance(value, (int, float, bool, str)) or value is None:
                data[name] = value
            elif isinstance(value, list):
                data[name] = list(value)
            elif isinstance(value, dict):
                data[name] = dict(value)
            else:
                data[name] = str(value)
        return data

    def get_owned_players():
        with get_save_manager().connection() as conn:
            cur = conn.execute("SELECT id FROM owned_players")
            return {row[0] for row in cur.fetchall()}

    owned = await asyncio.to_thread(get_owned_players)
    roster = []
    for name in player_plugins.__all__:
        cls = getattr(player_plugins, name)
        inst = cls()
        await asyncio.to_thread(_assign_damage_type, inst)
        if inst.id == "player":
            await asyncio.to_thread(_apply_player_customization, inst)
        stats = _serialize_stats(inst)
        roster.append(
            {
                "id": inst.id,
                "name": inst.name,
                "owned": inst.id in owned,
                "is_player": inst.id == "player",
                "element": inst.element_id,
                "stats": stats,
            }
        )
    return jsonify({"players": roster})


@bp.get("/player/stats")
async def player_stats() -> tuple[str, int, dict[str, object]]:
    refresh = _get_stat_refresh_rate()
    player = player_plugins.player.Player()
    await asyncio.to_thread(_assign_damage_type, player)
    
    # Store original stats before customization
    orig_stats = (player.max_hp, player.atk, player.defense)
    
    await asyncio.to_thread(_apply_player_customization, player)
    apply_status_hooks(player)
    
    # Log the stat changes for debugging
    log.debug(
        "Player stats endpoint: original=(%d, %d, %d), final=(%d, %d, %d), mods=%s",
        orig_stats[0],
        orig_stats[1], 
        orig_stats[2],
        player.max_hp,
        player.atk,
        player.defense,
        player.mods,
    )
    
    stats = {
        "core": {
            "hp": player.hp,
            "max_hp": player.max_hp,
            "exp": player.exp,
            "level": player.level,
            "exp_multiplier": player.exp_multiplier,
            "actions_per_turn": player.actions_per_turn,
        },
        "offense": {
            "atk": player.atk,
            "crit_rate": player.crit_rate,
            "crit_damage": player.crit_damage,
            "effect_hit_rate": player.effect_hit_rate,
            "damage_type": player.element_id,
        },
        "defense": {
            "defense": player.defense,
            "mitigation": player.mitigation,
            "regain": player.regain,
            "dodge_odds": player.dodge_odds,
            "effect_resistance": player.effect_resistance,
        },
        "vitality": {"vitality": player.vitality},
        "advanced": {
            "action_points": player.action_points,
            "damage_taken": player.damage_taken,
            "damage_dealt": player.damage_dealt,
            "kills": player.kills,
        },
        "status": {
            "passives": player.passives,
            "dots": player.dots,
            "hots": player.hots,
        },
    }
    return jsonify({"stats": stats, "refresh_rate": refresh})


@bp.get("/player/editor")
async def get_player_editor() -> tuple[str, int, dict[str, object]]:
    player = player_plugins.player.Player()
    await asyncio.to_thread(_assign_damage_type, player)
    pronouns, stats = await asyncio.to_thread(_load_player_customization)
    log.debug("Loading player editor data: pronouns=%s, stats=%s", pronouns, stats)
    return jsonify(
        {
            "pronouns": pronouns,
            "damage_type": player.element_id,
            "hp": stats.get("hp", 0),
            "attack": stats.get("attack", 0),
            "defense": stats.get("defense", 0),
        }
    )


@bp.put("/player/editor")
async def update_player_editor() -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    pronouns = (data.get("pronouns") or "").strip()
    damage_type = (data.get("damage_type") or "").capitalize()
    try:
        hp = int(data.get("hp", 0))
        attack = int(data.get("attack", 0))
        defense = int(data.get("defense", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid stats"}), 400
    total = hp + attack + defense
    if len(pronouns) > 15:
        return jsonify({"error": "invalid pronouns"}), 400
    allowed = {"Light", "Dark", "Wind", "Lightning", "Fire", "Ice"}
    if damage_type and damage_type not in allowed:
        return jsonify({"error": "invalid damage type"}), 400
    if total > 100:
        return jsonify({"error": "over-allocation"}), 400

    log.debug(
        "Updating player editor: pronouns=%s, damage_type=%s, hp=%d, attack=%d, defense=%d",
        pronouns,
        damage_type,
        hp,
        attack,
        defense,
    )

    def update_player_data():
        with get_save_manager().connection() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)",
                ("player_pronouns", pronouns),
            )
            conn.execute(
                "INSERT OR REPLACE INTO options (key, value) VALUES (?, ?)",
                (
                    "player_stats",
                    json.dumps({"hp": hp, "attack": attack, "defense": defense}),
                ),
            )
            if damage_type:
                conn.execute(
                    "INSERT OR REPLACE INTO damage_types (id, type) VALUES (?, ?)",
                    ("player", damage_type),
                )

    await asyncio.to_thread(update_player_data)
    log.debug("Player customization saved successfully")
    return jsonify({"status": "ok"})
