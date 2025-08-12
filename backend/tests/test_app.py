import json
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
    return app_module.app, db_path


@pytest.mark.asyncio
async def test_status_endpoint(app_with_db):
    app, _ = app_with_db
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 200
    data = await response.get_json()
    assert data == {"status": "ok"}


@pytest.mark.asyncio
async def test_run_flow(app_with_db):
    app, db_path = app_with_db
    client = app.test_client()

    start_resp = await client.post("/run/start")
    start_data = await start_resp.get_json()
    run_id = start_data["run_id"]

    await client.put(f"/party/{run_id}", json={"party": ["sample_player"]})

    map_resp = await client.get(f"/map/{run_id}")
    map_data = await map_resp.get_json()
    assert map_data["map"] == ["start", "battle", "boss"]

    conn = sqlcipher3.connect(db_path)
    conn.execute("PRAGMA key = 'testkey'")
    cur = conn.execute("SELECT party FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    assert json.loads(row[0]) == ["sample_player"]


@pytest.mark.asyncio
async def test_players_and_rooms(app_with_db):
    app, _ = app_with_db
    client = app.test_client()

    players_resp = await client.get("/players")
    players_data = await players_resp.get_json()
    assert any(p["id"] == "sample_player" and p["owned"] for p in players_data["players"])

    start_resp = await client.post("/run/start")
    run_id = (await start_resp.get_json())["run_id"]

    await client.put(f"/party/{run_id}", json={"party": ["sample_player"]})

    battle_resp = await client.post(f"/rooms/{run_id}/battle")
    assert battle_resp.status_code == 200
    battle_data = await battle_resp.get_json()
    assert "party" in battle_data and "foes" in battle_data
    assert battle_data["foes"][0]["hp"] <= 100

    shop_resp = await client.post(f"/rooms/{run_id}/shop")
    assert shop_resp.status_code == 200
    shop_data = await shop_resp.get_json()
    assert "party" in shop_data and shop_data["foes"] == []
    assert shop_data["party"][0]["gold"] >= 0

    rest_resp = await client.post(f"/rooms/{run_id}/rest")
    assert rest_resp.status_code == 200
    rest_data = await rest_resp.get_json()
    assert "party" in rest_data and rest_data["foes"] == []
    assert rest_data["party"][0]["hp"] == rest_data["party"][0]["max_hp"]
