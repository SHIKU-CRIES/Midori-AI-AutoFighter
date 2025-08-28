# Make web build playable (`7d79b17b`)

## Summary
Hook the Svelte frontend to the Quart backend so players can start runs and progress through rooms.

## Tasks
- [x] Expose backend APIs for party picking, player editing, map generation, and room actions.
- [x] Call these APIs from the frontend to drive the game flow.
- [x] Ensure state persists in the database between requests.
- [x] Document the flow in `.codex/implementation` and add backend tests.

## Context
Next step toward a fully playable web version.
