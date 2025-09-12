# Frontend: Display Action Queue

## Summary
Visualize turn order with portraits and optional Action Value numbers.

## Tasks
- Scaffold an `ActionQueue` component in the battle UI.
- Render combatant portraits in the order received from the backend.
- Highlight the portrait at the top as the active actor.
- Animate the active portrait moving to the bottom after its turn.
- Add a toggle in "Other Settings" to display Action Values.
- Show AV numbers beneath portraits when the toggle is enabled.
- Fetch queue state from the backend snapshot or a dedicated endpoint.
- Update the component whenever the queue data changes.
- Write tests for portrait ordering, movement animation, and the AV toggle.
- Document queue visuals and settings in battle UI and options docs.

## Acceptance Criteria
- Queue renders in battle UI with portraits moving as turns progress.
- AV numbers appear only when the setting is enabled.
- Animations respect reduced-motion settings.
- Tests demonstrate queue rendering and toggle behavior.
- Documentation reflects the new queue and options.

ready for review
