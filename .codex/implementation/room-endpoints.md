# Room Endpoints

The Quart backend exposes simple routes for core gameplay rooms. Each accepts the
current `run_id` and returns placeholder results until full game logic is wired.

## Routes

- `GET /players` – lists all plugin player characters with fields:
  - `id`: plugin identifier
  - `name`: display name
  - `owned`: whether the player owns this character
  - `is_player`: true for the player's avatar
- `POST /rooms/<run_id>/battle` – resolves a battle action.
- `POST /rooms/<run_id>/shop` – returns shop interactions.
- `POST /rooms/<run_id>/rest` – handles rest room actions.

All routes read and write state in the encrypted `save.db` using `AF_DB_PATH`
and `AF_DB_KEY`.

## Testing
- `uv run pytest backend/tests/test_app.py::test_players_and_rooms`
