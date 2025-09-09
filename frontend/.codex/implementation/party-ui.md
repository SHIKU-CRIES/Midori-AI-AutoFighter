# Party UI Improvements

This release improves clarity and accessibility in the Party overlay:

- Selected members are highlighted by a subtle, element‑tinted sweep placed
  beneath row content (photo, name, type). The effect starts smoothly, runs at
  a slow, randomized pace, and respects Reduced Motion (animation disabled,
  faint static highlight remains).
- The roster list no longer renders gray side borders; the stats panel on the
  right now fills its column.
- The Stats panel displays HP as `current/max` to make HP investment visible.

Implementation details:

- `PartyRoster.svelte` sets `--el-color` per row and derives `--el-dark`,
  `--el-5darker`, and `--el-5lighter` for a smooth gradient. The animated
  background is applied via `::before` and transitions opacity on selection to
  avoid abrupt starts.
- `PartyRoster.svelte` adds a header showing the number of selected party
  members (`X / 5`) and provides sorting controls for name, element, or id with
  an ascending/descending toggle. Selected members are always grouped at the
  top and sorted within their section.
- `PartyPicker.svelte` propagates `reducedMotion` to the roster so the effect
  can be disabled via Settings.
- `StatTabs.svelte` uses flexible sizing so the panel fills its side.
- `StatTabs.svelte` now embeds an `UpgradePanel` beneath the stats list,
  showing upgrade level and per-star item counts with a button disabled until
  enough materials are available (20×4★ or 100×3★ or 500×2★ or 1000×1★).
- `StatTabs.svelte` caches per-character stat editor values in a module-scoped
  `Map` keyed by character ID and persists allocations through
  `/players/<id>/editor` so non-player tweaks are saved across sessions and
  restored when reopening the editor or switching characters.

