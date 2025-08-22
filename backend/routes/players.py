from __future__ import annotations

import json

from dataclasses import asdict

from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.stats import apply_status_hooks

from plugins import players as player_plugins

from ..game import SAVE_MANAGER
from ..game import _apply_player_stats
from ..game import _assign_damage_type
from ..game import _load_player_customization

bp = Blueprint("players", __name__)


def _get_stat_refresh_rate() -> int:
    with SAVE_MANAGER.connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS options (key TEXT PRIMARY KEY, value TEXT)"
        )
        cur = conn.execute(
            "SELECT value FROM options WHERE key = ?", ("stat_refresh_rate",)
        )
        row = cur.fetchone()
    try:
        rate = int(row[0]) if row else 5
    except (TypeError, ValueError):
        rate = 5
    return max(1, min(rate, 10))


@bp.get("/players")
async def get_players() -> tuple[str, int, dict[str, str]]:
    with SAVE_MANAGER.connection() as conn:
        cur = conn.execute("SELECT id FROM owned_players")
        owned = {row[0] for row in cur.fetchall()}
    roster = []
    for name in player_plugins.__all__:
        cls = getattr(player_plugins, name)
        inst = cls()
        _assign_damage_type(inst)
        if inst.id == "player":
            _apply_player_stats(inst)
        stats = asdict(inst)
        stats["char_type"] = inst.char_type.name
        stats["damage_type"] = inst.element_id
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
    _assign_damage_type(player)
    _apply_player_stats(player)
    apply_status_hooks(player)
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
    _assign_damage_type(player)
    pronouns, stats = _load_player_customization()
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
    with SAVE_MANAGER.connection() as conn:
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
    return jsonify({"status": "ok"})
