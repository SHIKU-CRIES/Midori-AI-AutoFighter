# Crafting Menu

`CraftingMenu.svelte` fetches upgrade items from `/gacha` and renders them as a
left-to-right wrapping grid of item photos with a bottom-right count badge.
Names do not appear in the grid; they are shown only in the status/detail box on
the right when an item is selected. Manual crafting posts to `/gacha/craft`, and
the auto-craft toggle calls `/gacha/auto-craft`.

Items are stacked by element and star rank using `stackItems` so identical
materials collapse into a single grid tile with an updated count. Names are
normalized via `formatName` (e.g., `ice_4` → `Ice ★★★★`,
`lightning_3` → `Lightning ★★★`) for readability in the detail panel.

Selecting an item shows its current quantity alongside the amount required to
craft (125 for 1★–3★ upgrades, 10 for converting 4★ items into a ticket). The
Craft button remains disabled until at least one stack meets these thresholds,
preventing accidental calls when nothing can be upgraded.

Each grid tile displays an icon loaded from
`frontend/src/lib/assets/items/{element}/generic{rank}.png` with a colored
border and matching box shadow derived from the `--star-color` CSS variable
(gray→gold for 1–5★) so rarity remains visible even if artwork is missing. If an
icon fails to load, a safe fallback image from
`frontend/src/lib/assets/items/generic/generic1.png` is used.

Layout uses a two-column grid: the items grid fills the left column (wrapping
auto-fill tiles), and the fixed-width detail panel sits on the right so players
can inspect a material without losing their place.

## Testing
- `bun test`
