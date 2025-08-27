# Star-Rail Style Reward Overlay and UI Polish

## Summary
Rework the reward flow and card/relic presentation to mimic the Star Rail reference, introduce floating loot messages, and ensure asset loading is reliable.

## Tasks
- **Reward overlay redesign** ✅
  - Replace the current grid layout in `frontend/src/lib/RewardOverlay.svelte` with a Star Rail–style presentation.
  - Show at most three card choices, each with:
    - Name text at the top-left.
    - Top bar colored by star rank.
    - Centered icon.
    - Star rank indicators beneath the icon.
    - Description area and selectable button.
- **Dynamic card art builder** ✅
  - Create `CardArt.svelte` to layer the provided photo frame, star colors, and card icon.
  - Remove random placeholder art and use the builder for card visuals.
- **Curio-style relic panels** ✅
  - Introduce `CurioChoice.svelte` with circular relic art, star-colored header, and hover/focus effects.
  - Update `RewardOverlay.svelte` and `InventoryPanel.svelte` to use the new component.
- **Floating loot text** ✅
  - Add `FloatingLoot.svelte` and invoke it after battles so gold/items briefly float on screen.
  - Exclude loot from the reward overlay once displayed.
- **Reliable relic icons** ✅
  - Update `frontend/src/lib/rewardLoader.js` to map relic IDs to `assets/relics/{stars}/{id}.png` and handle missing assets gracefully.

## Context
Current reward UI feels janky and fails to load some assets. This overhaul aligns the experience with the Star Rail reference screenshot and clarifies card/relic selection.

## Testing
- `./run-tests.sh`
