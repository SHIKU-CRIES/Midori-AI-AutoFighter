# Backend: Implement Action Queue System

## Summary
Introduce an Action Gauge–based turn system in the backend battle loop.

## Tasks
- Add `action_gauge` and `action_value` fields to combatant data.
- Initialize each combatant's gauge to 10,000 at battle start.
- Compute base action value as `10,000 / SPD` and store it.
- Build a queue structure sorted by current action value.
- Provide a function to find the combatant with the lowest action value.
- After an actor finishes, reset its action value to the stored base value.
- Decrease action values of other combatants by the amount spent.
- Include queue data in the battle snapshot and/or create an `/action-queue` endpoint.
- Write unit tests covering speed-based ordering and post-turn reset.
- Document the queue mechanics in `.codex/implementation/battle-room.md`.

## Acceptance Criteria
- Backend determines turn order using Action Gauge/AV logic.
- Snapshot or endpoint returns queue data for all combatants.
- Tests cover basic speed and turn order scenarios.
- Documentation describes Action Queue behavior.

ready for review

