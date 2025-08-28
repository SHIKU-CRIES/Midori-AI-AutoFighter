# Retain party picker selections and persist to backend

## Summary
Persist party picker selections across component remounts and page reloads by syncing with the backend.

## Context
- Previous implementation reset selections after closing or reloading.
- `frontend/src/lib/PartyPicker.svelte` sets `selected = [player.id]` on mount, ignoring provided selections.
- Backend never stores the chosen party, so runs forget composition and ownership is unchecked.

## Tasks
1. Update `PartyPicker.svelte` so `onMount` only defaults to the player when `selected` is empty.
2. On confirmation, send selected character IDs to the backend to save the party for the active run.
3. Extend backend save/load logic to return the stored party and reject characters the player does not own.
4. Ensure `GameViewport` initializes `PartyPicker` with backend data so selections persist after closing and page refresh.
5. Add a frontend test that selects additional characters, closes and reopens the picker, refreshes the page, and asserts the selection persists.
6. Add a backend test that saves a party, reloads it, and fails when unowned characters are provided.
7. Run `bun test` and `uv run pytest` after changes.

## Acceptance Criteria
- Party choices survive closing and reopening the picker and refreshing the page.
- Backend stores and restores the party while refusing unowned characters.
- New tests confirm selection persistence and backend validation.
- `bun test` and `uv run pytest` executed.

Ready for review.
