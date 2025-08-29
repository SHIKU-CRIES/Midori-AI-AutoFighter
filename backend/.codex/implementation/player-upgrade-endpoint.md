# Player Upgrade Endpoint

`GET /players/<id>/upgrade` returns the current upgrade level for the
specified character and the full inventory of element-based upgrade items.

`POST /players/<id>/upgrade` consumes 20×4★ (or 100×3★/500×2★/1000×1★) items
matching the character's damage type and increments their stored level. Each
rank boosts HP, ATK, and DEF by 5% and persists in the `player_upgrades`
table. Item counts live in `upgrade_items`.

## Testing
- `uv run pytest backend/tests/test_player_upgrade.py`
