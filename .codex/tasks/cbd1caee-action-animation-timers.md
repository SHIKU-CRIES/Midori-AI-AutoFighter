# Action Animation Timers

## Summary
Associate each action with a duration and make the battle loop wait for animations to finish.

## Tasks
- Introduce an `animation_duration` property for actions and skills.
- Allow actions to specify per-target duration multipliers.
- Update the battle loop to await animation completion before starting the next action.
- Provide hooks or events for the frontend to start and finish animations.
- Scale wait time by target count for multi-target abilities.
- Write tests ensuring the loop waits the correct duration.
- Update `.codex/implementation/ui-animation-guidelines.md` with timing rules.

## Acceptance Criteria
- Actions block progression until their animation duration elapses.
- Multi-target actions scale their wait time appropriately.
- Tests validate that action timing is enforced.
- Documentation notes the timing system and any guidelines.
