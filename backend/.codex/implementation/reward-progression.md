# Reward progression and room advancement

The map state blocks advancing to the next room while any post-battle rewards remain unresolved. Three boolean flags gate this progression:

- `awaiting_card` – set when a card reward is offered. If the battle yields no card, this flag stays `False` and does not block advancement.
- `awaiting_relic` – set when a relic reward is pending. Runs without relic drops leave this flag `False`.
- `awaiting_loot` – reserved for manual loot flows. The backend currently auto-collects gold and similar drops, so this flag is usually `False`.

`advance_room` refuses to progress while any of these flags are `True`. The UI action handler returns an HTTP 400 error when a client attempts to advance with pending rewards, and the `run_service.advance_room` function raises a `ValueError` so direct calls cannot bypass the restriction.

Reward sequences may also use a `reward_progression` structure to handle multiple reward steps. Once all steps are completed and the `awaiting_*` flags are cleared, room advancement is allowed.
