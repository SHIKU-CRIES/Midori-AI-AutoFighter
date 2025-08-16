# Map Display

`MapDisplay.svelte` replaces the old `RunMap` and wraps the run's floor layout
in `MenuPanel`. The list is ordered with the current room at the bottom and the
boss at the top so the path reads upward. Each room is rendered as a
stained-glass button with a `lucide-svelte` icon matching its type (battle,
rest, shop, boss, or unknown). Only the current room is clickable and fully
opaque; upcoming rooms stay visible but are greyed out and disabled. The
component emits a `select` event when the player chooses the current room.

## Testing
- `bun test frontend/tests/mapdisplay.test.js`
