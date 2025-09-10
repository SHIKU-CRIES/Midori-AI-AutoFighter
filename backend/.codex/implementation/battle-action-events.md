# Battle action events

The battle system emits additional events to coordinate turn-based effects and
passive abilities:

- `action_used` – emitted from `rooms/battle.py` whenever a combatant completes
  an action.  Subscribers receive the acting entity, the target, and the amount
  of damage or healing dealt.
- `extra_turn` – grants an immediate extra action to the recipient.  The battle
  loop tracks pending turns so effects like **SwiftFootwork** or **EchoBell** can
  schedule additional moves without creating infinite loops.
- `summon_created` – emitted when a summon enters play.
- `summon_removed` – emitted when a summon leaves play for any reason.
- `summon_defeated` – emitted after a summon is killed and removed, allowing
  passives like **Menagerie Bond** to respond.

Damage type ultimates now consume charge via `use_ultimate()` and are invoked by
`rooms/battle.py` when `ultimate_ready` is set.  Damage type plugins may add
additional effects in their `ultimate` methods or respond to the
`ultimate_used` event.

## Pacing

Each action calls the internal `_pace` helper, which yields for roughly half a
second based on the time spent executing the move. This per-actor pacing keeps
combat readable while avoiding full-turn delays.
