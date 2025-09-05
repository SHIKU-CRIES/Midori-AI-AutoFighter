# Run Helpers

- `src/lib/runState.js`: utilities for saving and loading run identifiers in `localStorage`.
- `src/lib/systems/uiApi.js`: primary UI-centric API for starting runs,
  performing room actions, advancing rooms, updating parties, fetching battle
  summaries/events, catalog lookups, and selecting rewards.
  `handleFetch` normalizes backend errors and reports them via the overlay
  system.
  `advanceRoom` first loads the current run state and refuses to send the
  action while any `awaiting_*` reward flags are true, preventing accidental
  progression past unclaimed rewards.
- The legacy `runApi.js` module has been removed; all callers should use
  the `uiApi` helpers.
- `src/lib/MainMenu.svelte`: renders the stained glass side menu from a list of items.
- `src/lib/RunButtons.svelte`: module script exporting `buildRunMenu` for constructing the menu item list. Inventory was removed from this menu and moved to the in‑run NavBar.
- `src/lib/api.js`: `getBackendFlavor()` reports which backend flavor is active.
- `src/routes/+page.svelte` now coordinates these helpers and avoids direct `localStorage` or fetch logic, also checking the backend flavor on mount.
- `enterRoom` wraps `roomAction` calls with error handling. If the request fails, it attempts to load the latest battle snapshot and alerts the user when recovery is not possible. A `404` response clears the stored run state and returns the player to the main menu so restarting is possible.
- `NavBar.svelte` now exposes an in‑run Inventory button (disabled during battles) alongside Home/Battle, Editor, Settings, and Back.
