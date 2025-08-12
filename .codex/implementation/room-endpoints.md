# Room Endpoints

The Quart backend exposes routes for core gameplay rooms. Each accepts the
current `run_id` and returns data generated from the existing plugin system.

## Routes

- `GET /players` – lists all plugin player characters with fields:
  - `id`: plugin identifier
  - `name`: display name
  - `owned`: whether the player owns this character
  - `is_player`: true for the player's avatar
- `POST /rooms/<run_id>/battle` – loads the player's party and a sample foe
  plugin, applies each member's attack to the foe, and returns the updated foe
  HP alongside party stats.
- `POST /rooms/<run_id>/shop` – echoes the party with current gold values for
  purchasing logic.
- `POST /rooms/<run_id>/rest` – heals the party to full and returns their HP
  and maximum HP.

All routes read and write state in the encrypted `save.db` using `AF_DB_PATH`
and `AF_DB_KEY`.

## Testing
- `uv run pytest backend/tests/test_app.py::test_players_and_rooms`
