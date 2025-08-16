# Apply DoT chance with effect stats and emit combat events

## Summary
- Damage types now roll `effect_hit_rate` against `effect_resistance` to attach element-themed DoTs scaled by damage dealt
- Stats emit `damage_taken`, `damage_dealt`, `heal_received`, and `heal` events so dots, hots, relics, and cards can react

## Testing
- `uv venv`
- `cd backend && uv sync`
- `cd backend && uv run pytest`
- `cd frontend && bun install`
- `cd frontend && bun test`
