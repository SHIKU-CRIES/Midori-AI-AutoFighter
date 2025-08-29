import importlib.util
from pathlib import Path

import pytest
import sqlcipher3


@pytest.fixture()
def app_with_db(tmp_path, monkeypatch):
    db_path = tmp_path / "save.db"
    monkeypatch.setenv("AF_DB_PATH", str(db_path))
    monkeypatch.setenv("AF_DB_KEY", "testkey")
    monkeypatch.syspath_prepend(Path(__file__).resolve().parents[1])
    spec = importlib.util.spec_from_file_location(
        "app", Path(__file__).resolve().parents[1] / "app.py",
    )
    app_module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(app_module)
    app_module.app.testing = True
    conn = sqlcipher3.connect(db_path)
    conn.execute("PRAGMA key = 'testkey'")
    conn.execute(
        "INSERT OR REPLACE INTO damage_types (id, type) VALUES (?, ?)",
        ("player", "fire"),
    )
    conn.execute(
        "INSERT OR REPLACE INTO upgrade_items (id, count) VALUES (?, ?)",
        ("fire_4", 20),
    )
    conn.commit()
    conn.close()
    return app_module.app, db_path


@pytest.mark.asyncio
async def test_upgrade_increases_stats(app_with_db):
    app, db_path = app_with_db
    client = app.test_client()

    resp = await client.post("/players/player/upgrade")
    data = await resp.get_json()
    assert data["level"] == 1
    assert data["items"].get("fire_4", 0) == 0

    resp = await client.get("/players/player/upgrade")
    data = await resp.get_json()
    assert data["level"] == 1

    resp = await client.get("/players")
    roster = await resp.get_json()
    player_entry = next(p for p in roster["players"] if p["id"] == "player")
    assert player_entry["stats"]["max_hp"] > 1000

    conn = sqlcipher3.connect(db_path)
    conn.execute("PRAGMA key = 'testkey'")
    cur = conn.execute("SELECT level FROM player_upgrades WHERE id = ?", ("player",))
    assert cur.fetchone()[0] == 1
    conn.close()

