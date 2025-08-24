# Run Helpers

- `src/lib/runState.js`: utilities for saving and loading run identifiers in `localStorage`.
- `src/lib/runApi.js`: thin wrappers around backend endpoints used during a run (start, room actions, rewards).
- `src/lib/MainMenu.svelte`: renders the stained glass side menu from a list of items.
- `src/lib/RunButtons.svelte`: module script exporting `buildRunMenu` for constructing the menu item list.
- `src/lib/api.js`: `getBackendFlavor()` reports which backend flavor is active.
- `src/routes/+page.svelte` now coordinates these helpers and avoids direct `localStorage` or fetch logic, also checking the backend flavor on mount.
- `enterRoom` wraps `roomAction` calls with error handling. If the request fails, it attempts to load the latest battle snapshot and alerts the user when recovery is not possible.
