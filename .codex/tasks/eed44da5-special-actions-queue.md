# Special Actions in Action Queue

## Summary
Handle immediate actions, ultimate interrupts, and extra actions within the queue.

## Tasks
- Allow abilities to flag a unit for an immediate extra turn.
- Move flagged units to the front of the queue when triggered.
- Display a banner overlay when an ultimate interrupts turn order.
- Insert an extra portrait at the top when a bonus turn is granted.
- Animate immediate actions and bonus turns with distinctive effects.
- Keep backend and frontend queue state synchronized during these events.
- Add tests for immediate actions, ultimates, and bonus turns.
- Document queue-manipulating abilities in `.codex/implementation/battle-room.md` and related files.

## Acceptance Criteria
- Immediate-action skills move the unit to the queue front.
- Ultimates display a banner and run without breaking base turn order.
- Extra turns visibly insert the unit at the top and execute correctly.
- Tests cover immediate actions, ultimates, and bonus turns.
- Documentation explains queue-manipulating abilities.

ready for review
