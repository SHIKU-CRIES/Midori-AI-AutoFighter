from __future__ import annotations

import os
import json
from pathlib import Path
from uuid import uuid4

import sqlcipher3

from quart import Quart
from quart import jsonify
from quart import request

from plugins import players as player_plugins


DB_PATH = Path(
    os.getenv("AF_DB_PATH", Path(__file__).resolve().parents[1] / "save.db")
)
DB_KEY = os.getenv("AF_DB_KEY", "")


def connect_db() -> sqlcipher3.Connection:
    conn = sqlcipher3.connect(DB_PATH)
    conn.execute(f"PRAGMA key = '{DB_KEY}'")
    return conn


def init_db() -> None:
    conn = connect_db()
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, party TEXT, map TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS owned_players (id TEXT PRIMARY KEY)"
        )
        cur = conn.execute("SELECT COUNT(*) FROM owned_players")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO owned_players (id) VALUES (?)",
                [("sample_player",), ("becca",)],
            )


init_db()

app = Quart(__name__)


@app.get("/")
async def status() -> tuple[str, int, dict[str, str]]:
    return jsonify({"status": "ok"})


@app.post("/run/start")
async def start_run() -> tuple[str, int, dict[str, str]]:
    conn = connect_db()
    run_id = str(uuid4())
    game_map = ["start", "battle", "boss"]
    with conn:
        conn.execute(
            "INSERT INTO runs (id, party, map) VALUES (?, ?, ?)",
            (run_id, json.dumps([]), json.dumps(game_map)),
        )
    return jsonify({"run_id": run_id, "map": game_map})


@app.put("/party/<run_id>")
async def update_party(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    party = data.get("party", [])
    conn = connect_db()
    with conn:
        conn.execute(
            "UPDATE runs SET party = ? WHERE id = ?",
            (json.dumps(party), run_id),
        )
    return jsonify({"status": "ok"})


@app.get("/map/<run_id>")
async def get_map(run_id: str) -> tuple[str, int, dict[str, str]]:
    conn = connect_db()
    cur = conn.execute("SELECT map FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    if row is None:
        return jsonify({"error": "run not found"}), 404
    return jsonify({"map": json.loads(row[0])})


@app.get("/players")
async def get_players() -> tuple[str, int, dict[str, str]]:
    conn = connect_db()
    cur = conn.execute("SELECT id FROM owned_players")
    owned = {row[0] for row in cur.fetchall()}
    roster = []
    for name in player_plugins.__all__:
        cls = getattr(player_plugins, name)
        roster.append(
            {
                "id": cls.id,
                "name": cls.name,
                "owned": cls.id in owned,
                "is_player": cls.id == "sample_player",
            }
        )
    return jsonify({"players": roster})


@app.post("/rooms/<run_id>/battle")
async def battle_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify({"run_id": run_id, "result": "battle", "action": data.get("action", "")})


@app.post("/rooms/<run_id>/shop")
async def shop_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify({"run_id": run_id, "result": "shop", "action": data.get("action", "")})


@app.post("/rooms/<run_id>/rest")
async def rest_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify({"run_id": run_id, "result": "rest", "action": data.get("action", "")})


@app.post("/rooms/<run_id>/<room_id>/action")
async def room_action(run_id: str, room_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify({"run_id": run_id, "room_id": room_id, "action": data.get("action", "noop")})


if __name__ == "__main__":
    app.run(port=59002)

