from __future__ import annotations

import os
import json
from pathlib import Path
from uuid import uuid4

import sqlcipher3

from quart import Quart
from quart import jsonify
from quart import request
from quart import send_from_directory
from quart import url_for

from plugins import players as player_plugins
from plugins.foes.sample_foe import SampleFoe


DB_PATH = Path(
    os.getenv("AF_DB_PATH", Path(__file__).resolve().parent / "save.db")
)
DB_KEY = os.getenv("AF_DB_KEY", "")


def connect_db() -> sqlcipher3.Connection:
    # Try to open with encryption key if provided; otherwise open plaintext.
    if DB_KEY:
        try:
            conn = sqlcipher3.connect(DB_PATH)
            conn.execute(f"PRAGMA key = '{DB_KEY}'")
            # Touch the database to validate key usage
            conn.execute("PRAGMA user_version")
            return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            # Fallback to plaintext if the file is not encrypted
            conn = sqlcipher3.connect(DB_PATH)
            return conn
    else:
        # No key provided: open as plaintext
        return sqlcipher3.connect(DB_PATH)


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


# Expose static assets (e.g., backgrounds) for simple image serving
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


@app.get("/assets/<path:filename>")
async def assets(filename: str):
    return await send_from_directory(ASSETS_DIR, filename)


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


@app.get("/rooms/images")
async def room_images() -> tuple[str, int, dict[str, str]]:
    # Basic mapping of room types to background images
    mapping = {
        "battle": "textures/backgrounds/background_01.png",
        "shop": "textures/backgrounds/background_02.png",
        "rest": "textures/backgrounds/background_03.png",
    }
    images = {key: f"/assets/{rel}" for key, rel in mapping.items()}
    return jsonify({"images": images})


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


def load_party(run_id: str) -> list[player_plugins.PlayerBase]:
    conn = connect_db()
    cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    party_ids = json.loads(row[0]) if row else []
    members: list[player_plugins.PlayerBase] = []
    for pid in party_ids:
        for name in player_plugins.__all__:
            cls = getattr(player_plugins, name)
            if cls.id == pid:
                members.append(cls())
                break
    return members


@app.post("/rooms/<run_id>/battle")
async def battle_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    party = load_party(run_id)
    foe = SampleFoe()
    foe_hp = 100
    for member in party:
        foe_hp -= member.atk
    foes = [{"id": foe.id, "hp": max(foe_hp, 0)}]
    party_data = [{"id": p.id, "hp": p.hp, "atk": p.atk} for p in party]
    return jsonify(
        {
            "run_id": run_id,
            "result": "battle",
            "party": party_data,
            "foes": foes,
            "action": data.get("action", ""),
        }
    )


@app.post("/rooms/<run_id>/shop")
async def shop_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    party = load_party(run_id)
    party_data = [{"id": p.id, "gold": p.gold} for p in party]
    return jsonify(
        {
            "run_id": run_id,
            "result": "shop",
            "party": party_data,
            "foes": [],
            "action": data.get("action", ""),
        }
    )


@app.post("/rooms/<run_id>/rest")
async def rest_room(run_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    party = load_party(run_id)
    for member in party:
        member.hp = member.max_hp
    party_data = [{"id": p.id, "hp": p.hp, "max_hp": p.max_hp} for p in party]
    return jsonify(
        {
            "run_id": run_id,
            "result": "rest",
            "party": party_data,
            "foes": [],
            "action": data.get("action", ""),
        }
    )


@app.post("/rooms/<run_id>/<room_id>/action")
async def room_action(run_id: str, room_id: str) -> tuple[str, int, dict[str, str]]:
    data = await request.get_json(silent=True) or {}
    return jsonify({"run_id": run_id, "room_id": room_id, "action": data.get("action", "noop")})


if __name__ == "__main__":
    app.run(port=59002)
