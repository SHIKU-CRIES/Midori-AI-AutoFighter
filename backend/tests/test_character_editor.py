import importlib.util
from pathlib import Path

import pytest


@pytest.fixture()
def app_with_db(tmp_path, monkeypatch):
    db_path = tmp_path / "save.db"
    monkeypatch.setenv("AF_DB_PATH", str(db_path))
    monkeypatch.setenv("AF_DB_KEY", "testkey")
    monkeypatch.syspath_prepend(Path(__file__).resolve().parents[1])
    spec = importlib.util.spec_from_file_location(
        "app",
        Path(__file__).resolve().parents[1] / "app.py",
    )
    app_module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(app_module)
    app_module.app.testing = True
    return app_module.app


@pytest.mark.asyncio
async def test_character_editor_luna(app_with_db):
    app = app_with_db
    client = app.test_client()

    resp = await client.put(
        "/players/luna/editor",
        json={
            "hp": 10,
            "attack": 20,
            "defense": 30,
            "crit_rate": 10,
            "crit_damage": 5,
        },
    )
    assert resp.status_code == 200

    data = await client.get("/players/luna/editor")
    payload = await data.get_json()
    assert payload == {
        "hp": 10,
        "attack": 20,
        "defense": 30,
        "crit_rate": 10,
        "crit_damage": 5,
    }

    roster_resp = await client.get("/players")
    roster = await roster_resp.get_json()
    luna = next(p for p in roster["players"] if p["id"] == "luna")
    core = luna["stats"]["core"]
    offense = luna["stats"]["offense"]
    defense_block = luna["stats"]["defense"]
    assert core["hp"] == 1100 and core["max_hp"] == 1100
    assert offense["atk"] == 120
    assert defense_block["defense"] == 65
    assert offense["crit_rate"] == pytest.approx(0.0575, rel=1e-3)
    assert offense["crit_damage"] == pytest.approx(2.1, rel=1e-3)
