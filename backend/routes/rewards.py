from __future__ import annotations

from quart import Blueprint
from quart import jsonify
from quart import request
from services.reward_service import acknowledge_loot as acknowledge_loot_service
from services.reward_service import select_card as select_card_service
from services.reward_service import select_relic as select_relic_service

bp = Blueprint("rewards", __name__)


@bp.post("/rewards/cards/<run_id>")
async def select_card(run_id: str):
    data = await request.get_json(silent=True) or {}
    card_id = data.get("card")
    try:
        result = await select_card_service(run_id, card_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


@bp.post("/rewards/relics/<run_id>")
async def select_relic(run_id: str):
    data = await request.get_json(silent=True) or {}
    relic_id = data.get("relic")
    try:
        result = await select_relic_service(run_id, relic_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


@bp.post("/rewards/loot/<run_id>")
async def acknowledge_loot(run_id: str):
    try:
        result = await acknowledge_loot_service(run_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)
