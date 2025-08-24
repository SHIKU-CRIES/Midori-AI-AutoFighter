# Battle snapshots

Battle resolution updates in `game._run_battle` ensure the frontend can safely
poll for results:

- Final snapshots now include an `awaiting_next` flag indicating whether the
  next room can be entered without card or relic choices.
- Reward processing is wrapped in a `try/except`. If an exception occurs, the
  snapshot is populated with any available loot, an `error` message, and
  `awaiting_next` set to `false` so clients are not blocked waiting for results.
- The call to `room.resolve` is wrapped in a `try/except` to guard against
  crashes. On failure the battle flag is cleared, map and party data are saved,
  and the snapshot records the `error` with `awaiting_next` set to `false` so
  runs do not hang.

These snapshots are stored in `game.battle_snapshots` and polled by the
frontend during combat.

