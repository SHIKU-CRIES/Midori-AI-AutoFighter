# Responsive Layout for Svelte UI

## Summary
Add responsive breakpoints so the frontend adapts to desktop, tablet, and phone screens.

## Tasks
- Show party picker, player editor, and a stats panel alongside the active menu on desktop viewports.
- Display two panels side by side on tablets when space allows.
- Restrict phones to a single menu at a time for clarity.
- Update `.codex/implementation` docs and add tests covering layout behavior.

## Acceptance Criteria
- Desktop renders party picker, player editor, stats panel, and menu together.
- Tablets show the menu beside one additional panel.
- Phones show only one menu at a time.
- `bun test` includes layout visibility checks and passes.
