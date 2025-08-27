from __future__ import annotations

import logging
import os
import traceback

# Import torch checker early to perform the one-time check
from llms.torch_checker import is_torch_available

from game import GachaManager  # noqa: F401  # re-export for tests
from game import _apply_player_customization  # noqa: F401
from game import _assign_damage_type  # noqa: F401
from game import _load_player_customization  # noqa: F401
from game import _passive_names  # noqa: F401
from game import _run_battle  # noqa: F401
from game import _scale_stats  # noqa: F401
from game import battle_snapshots  # noqa: F401
from game import battle_tasks  # noqa: F401
from game import get_fernet  # noqa: F401
from game import get_save_manager  # noqa: F401
from game import load_map  # noqa: F401
from game import load_party  # noqa: F401
from game import save_map  # noqa: F401
from game import save_party  # noqa: F401
from logging_config import configure_logging
from quart import Quart
from quart import jsonify
from quart import request
from routes.assets import bp as assets_bp
from routes.config import bp as config_bp
from routes.catalog import bp as catalog_bp
from routes.gacha import bp as gacha_bp
from routes.players import bp as players_bp
from routes.rewards import bp as rewards_bp
from routes.rooms import bp as rooms_bp
from routes.runs import bp as runs_bp

configure_logging()

log = logging.getLogger(__name__)

# Log torch availability status on startup
log.info("Torch availability check: %s", "available" if is_torch_available() else "not available")

app = Quart(__name__)
app.register_blueprint(assets_bp)
app.register_blueprint(gacha_bp)
app.register_blueprint(players_bp)
app.register_blueprint(runs_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(rewards_bp)
app.register_blueprint(config_bp)
app.register_blueprint(catalog_bp)

BACKEND_FLAVOR = os.getenv("UV_EXTRA", "default")


@app.get("/")
async def status() -> tuple[str, int, dict[str, str]]:
    return jsonify({"status": "ok", "flavor": BACKEND_FLAVOR})


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


@app.errorhandler(Exception)
async def handle_exception(e: Exception):
    log.exception(e)
    tb = traceback.format_exc()
    response = jsonify({"error": str(e), "traceback": tb})
    response.status_code = 500
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=59002)
