# Reward Overlay

After a battle resolves, the backend may return `card_choices`. `GameViewport.svelte` detects these and opens `RewardOverlay.svelte` inside an `OverlaySurface`. The overlay displays each option's art pulled from `.codex/downloads` folders and lets the player pick a reward.

Selecting a card posts to `/cards/<run_id>` via the `chooseCard` API helper and clears `card_choices` so the run can proceed to the next room.

## Testing
- `bun test`
