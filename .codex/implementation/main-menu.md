# Main Menu

The Svelte front page presents a high-contrast grid of icon buttons inspired by
Arknights. Menu items include **Run**, **Party**, **Settings**, and **Stats**, each
showing a Lucide icon above a label. Layout is determined by `layoutForWidth`:
- **Desktop:** menu grid with PartyPicker, PlayerEditor, and StatsPanel panels
  alongside it.
- **Tablet:** menu grid beside the PartyPicker panel.
- **Phone:** only the menu grid is shown for clarity.

Choosing **Run** opens a modal PartyPicker so the player confirms their lineup
before the `RunMap` component appears.

## Testing
- `bun test frontend/tests/layout.test.js`
