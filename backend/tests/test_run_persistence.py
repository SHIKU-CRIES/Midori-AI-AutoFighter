"""Test run persistence across backend restarts."""

import json
from pathlib import Path
import sys
import tempfile
import time

import pytest

sys.path.append(str(Path(__file__).parent.parent))

import game
from game import get_save_manager


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global state before and after each test."""
    original_save_manager = game.SAVE_MANAGER
    original_fernet = game.FERNET
    game.SAVE_MANAGER = None
    game.FERNET = None
    yield
    game.SAVE_MANAGER = original_save_manager
    game.FERNET = original_fernet


def test_run_persistence_across_restart():
    """Test that runs persist in database across backend restart simulation."""
    # Use a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = Path(tmp_db.name)

    try:
        # Simulate first backend instance
        import os
        original_db_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

        # Reset global state to force re-initialization
        game.SAVE_MANAGER = None
        game.FERNET = None

        # Get save manager (this will create the database)
        manager1 = get_save_manager()

        # Create a test run
        run_id = f'test-run-{int(time.time())}'  # Use timestamp to make it unique
        party_data = {
            "members": ["player"],
            "gold": 100,
            "relics": [],
            "cards": [],
            "exp": {"player": 0},
            "level": {"player": 1},
            "rdr": 1.0,
            "player": {"pronouns": "", "damage_type": "Light", "stats": {"hp": 0, "attack": 0, "defense": 0}}
        }
        map_data = {
            "rooms": [{"room_type": "start"}, {"room_type": "battle-normal"}],
            "current": 1,
            "battle": False,
            "awaiting_card": False,
            "awaiting_relic": False,
            "awaiting_next": False,
        }

        with manager1.connection() as conn:
            conn.execute(
                "INSERT INTO runs (id, party, map) VALUES (?, ?, ?)",
                (run_id, json.dumps(party_data), json.dumps(map_data))
            )

        # Verify run exists
        with manager1.connection() as conn:
            cur = conn.execute("SELECT id, party, map FROM runs WHERE id = ?", (run_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == run_id

        # Simulate backend restart by resetting global state
        game.SAVE_MANAGER = None
        game.FERNET = None

        # Get save manager again (simulating new backend instance)
        manager2 = get_save_manager()

        # Verify run still exists after "restart"
        with manager2.connection() as conn:
            cur = conn.execute("SELECT id, party, map FROM runs WHERE id = ?", (run_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == run_id

            # Verify data integrity
            loaded_party = json.loads(row[1])
            loaded_map = json.loads(row[2])
            assert loaded_party["members"] == ["player"]
            assert loaded_party["gold"] == 100
            assert loaded_map["current"] == 1
            assert loaded_map["battle"] is False

    finally:
        # Clean up
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)
        db_path.unlink(missing_ok=True)


def test_get_map_endpoint_after_restart():
    """Test that the /map/<run_id> endpoint works after restart."""
    import asyncio

    from routes.runs import get_map

    # Use a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = Path(tmp_db.name)

    try:
        # Simulate first backend instance
        import os
        original_db_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

        # Reset global state to force re-initialization
        game.SAVE_MANAGER = None
        game.FERNET = None

        # Get save manager (this will create the database)
        manager1 = get_save_manager()

        # Create a test run
        run_id = 'test-run-456'
        party_data = {
            "members": ["player"],
            "gold": 50,
            "relics": [],
            "cards": [],
            "exp": {"player": 10},
            "level": {"player": 1},
            "rdr": 1.0,
            "player": {"pronouns": "", "damage_type": "Fire", "stats": {"hp": 0, "attack": 0, "defense": 0}}
        }
        map_data = {
            "rooms": [{"room_type": "start"}, {"room_type": "battle-normal"}, {"room_type": "rest"}],
            "current": 2,
            "battle": False,
            "awaiting_card": False,
            "awaiting_relic": False,
            "awaiting_next": True,
        }

        with manager1.connection() as conn:
            conn.execute(
                "INSERT INTO runs (id, party, map) VALUES (?, ?, ?)",
                (run_id, json.dumps(party_data), json.dumps(map_data))
            )

        # Simulate backend restart
        game.SAVE_MANAGER = None
        game.FERNET = None

        # Test the get_map endpoint
        async def test_endpoint():
            response_data, status_code, headers = await get_map(run_id)
            response_json = response_data.get_json()

            assert status_code == 200
            assert "map" in response_json
            assert "party" in response_json
            assert response_json["map"]["current"] == 2
            assert response_json["map"]["awaiting_next"] is True
            assert response_json["party"] == ["player"]

        asyncio.run(test_endpoint())

    finally:
        # Clean up
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)
        db_path.unlink(missing_ok=True)


def test_run_not_found():
    """Test that non-existent runs return 404."""
    import asyncio

    from routes.runs import get_map

    # Use a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = Path(tmp_db.name)

    try:
        import os
        original_db_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

        # Reset global state
        game.SAVE_MANAGER = None
        game.FERNET = None

        # Initialize empty database
        get_save_manager()

        # Test with non-existent run
        async def test_endpoint():
            response_data, status_code, headers = await get_map('nonexistent-run')
            assert status_code == 404

        asyncio.run(test_endpoint())

    finally:
        # Clean up
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)
        db_path.unlink(missing_ok=True)
