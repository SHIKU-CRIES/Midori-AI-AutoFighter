# Improve battle stats readability

## Summary
Place battle stats within stained-glass containers to improve contrast and follow the UI theme.

## Context
- Earlier fix omitted stained-glass backgrounds, leaving text hard to read over the battlefield.
- Navigation elements use stained-glass styles (e.g., `.stained-glass-bar`, `.stained-glass-side`), and the UI foundation plan calls for frosted glass surfaces.

## Tasks
1. Wrap the party and foe stat sections in `frontend/src/lib/BattleView.svelte` with resizable stained-glass containers that match existing top-bar and sidebar styling.
2. Reuse or extract shared stained-glass CSS so both containers share gradients, borders, and backdrop blur.
3. Ensure layout adapts to viewport size, keeping portraits and HP bars visible without overlap.
4. Update CSS and layout for readability on desktop and mobile.
5. Add a frontend test verifying that stained-glass container classes render for both party and foe sections.
6. Run `bun test` and `uv run pytest` after changes.

## Acceptance Criteria
- Stats for both allies and foes appear within stained-glass containers and remain legible across screen sizes.
- New test confirms container classes render.
- `bun test` and `uv run pytest` executed.

Ready for review.
