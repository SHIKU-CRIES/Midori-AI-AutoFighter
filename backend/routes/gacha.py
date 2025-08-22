from __future__ import annotations

from dataclasses import asdict

from quart import Blueprint
from quart import jsonify
from quart import request

from autofighter.gacha import GachaManager

from ..game import SAVE_MANAGER

bp = Blueprint("gacha", __name__)


@bp.get("/gacha")
async def gacha_state() -> tuple[str, int, dict[str, object]]:
    manager = GachaManager(SAVE_MANAGER)
    return jsonify(manager.get_state())


@bp.post("/gacha/pull")
async def gacha_pull() -> tuple[str, int, dict[str, object]]:
    data = await request.get_json(silent=True) or {}
    count = int(data.get("count", 1))
    manager = GachaManager(SAVE_MANAGER)
    try:
        results = manager.pull(count)
    except ValueError:
        return jsonify({"error": "invalid count"}), 400
    except PermissionError:
        return jsonify({"error": "insufficient tickets"}), 403
    state = manager.get_state()
    state["results"] = [asdict(r) for r in results]
    return jsonify(state)


@bp.post("/gacha/auto-craft")
async def gacha_auto_craft() -> tuple[str, int, dict[str, object]]:
    data = await request.get_json(silent=True) or {}
    enabled = bool(data.get("enabled"))
    manager = GachaManager(SAVE_MANAGER)
    manager.set_auto_craft(enabled)
    return jsonify({"status": "ok", "auto_craft": enabled})


@bp.post("/gacha/craft")
async def gacha_craft() -> tuple[str, int, dict[str, object]]:
    manager = GachaManager(SAVE_MANAGER)
    items = manager.craft()
    return jsonify({"status": "ok", "items": items})
