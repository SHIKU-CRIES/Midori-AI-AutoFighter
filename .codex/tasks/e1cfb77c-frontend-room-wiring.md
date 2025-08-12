# Wire Svelte UI to room endpoints (`e1cfb77c`)

## Summary
Connect the Svelte frontend to battle, shop, and rest endpoints to handle actions and show results.

## Tasks
- Call the new backend endpoints for each room.
- Display room outcomes and updated party data.
- Render foes along the top row with their stat bars while player characters show their ultimate circles as described in `feedback.md`.
- Limit battle rooms to ten foes on desktop and tablet screens but only three on phones.
- Keep room views 16:9 on desktop and tablet, scaling to full phone size on mobile.
- Update `myunderstanding.md` and relevant implementation docs.

## Context
Completes the loop between the web UI and game logic.
