from __future__ import annotations

from quart import Quart
from quart import jsonify
from quart import request

from routes.assets import bp as assets_bp
from routes.gacha import bp as gacha_bp
from routes.players import bp as players_bp
from routes.rewards import bp as rewards_bp
from routes.rooms import bp as rooms_bp
from routes.runs import bp as runs_bp

from game import FERNET
from game import GachaManager  # re-export for tests
from game import SAVE_MANAGER
from game import _apply_player_stats
from game import _assign_damage_type
from game import _load_player_customization
from game import _passive_names
from game import _run_battle
from game import battle_snapshots
from game import battle_tasks
from game import load_map
from game import load_party
from game import save_map
from game import save_party

app = Quart(__name__)
app.register_blueprint(assets_bp)
app.register_blueprint(gacha_bp)
app.register_blueprint(players_bp)
app.register_blueprint(runs_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(rewards_bp)


@app.get("/")
async def status() -> tuple[str, int, dict[str, str]]:
    return jsonify({"status": "ok"})


@app.after_request
async def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.before_request
async def handle_cors_preflight():
    if request.method == "OPTIONS":
        return "", 204
