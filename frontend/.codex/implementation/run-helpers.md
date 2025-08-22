# Run Helpers

- `src/lib/runState.js`: utilities for saving and loading run identifiers in `localStorage`.
- `src/lib/runApi.js`: thin wrappers around backend endpoints used during a run (start, room actions, rewards).
- `src/lib/MainMenu.svelte`: renders the stained glass side menu from a list of items.
- `src/lib/RunButtons.svelte`: module script exporting `buildRunMenu` for constructing the menu item list.
- `src/routes/+page.svelte` now coordinates these helpers and avoids direct `localStorage` or fetch logic.
