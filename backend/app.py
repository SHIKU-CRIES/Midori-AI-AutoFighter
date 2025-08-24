from __future__ import annotations

import os
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler

from quart import Quart
from quart import jsonify
from quart import request

from routes.runs import bp as runs_bp
from routes.gacha import bp as gacha_bp
from routes.rooms import bp as rooms_bp
from routes.assets import bp as assets_bp
from routes.players import bp as players_bp
from routes.rewards import bp as rewards_bp

from game import FERNET  # noqa: F401
from game import GachaManager  # noqa: F401  # re-export for tests
from game import SAVE_MANAGER  # noqa: F401
from game import _apply_player_stats  # noqa: F401
from game import _assign_damage_type  # noqa: F401
from game import _load_player_customization  # noqa: F401
from game import _passive_names  # noqa: F401
from game import _run_battle  # noqa: F401
from game import _scale_stats  # noqa: F401
from game import battle_snapshots  # noqa: F401
from game import battle_tasks  # noqa: F401
from game import load_map  # noqa: F401
from game import load_party  # noqa: F401
from game import save_map  # noqa: F401
from game import save_party  # noqa: F401

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

file_handler = RotatingFileHandler(
    LOG_DIR / "backend.log", maxBytes=1_048_576, backupCount=5
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)

log = logging.getLogger(__name__)

app = Quart(__name__)
app.register_blueprint(assets_bp)
app.register_blueprint(gacha_bp)
app.register_blueprint(players_bp)
app.register_blueprint(runs_bp)
app.register_blueprint(rooms_bp)
app.register_blueprint(rewards_bp)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=59002)
