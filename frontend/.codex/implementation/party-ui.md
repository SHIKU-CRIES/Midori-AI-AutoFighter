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
- `PartyPicker.svelte` propagates `reducedMotion` to the roster so the effect
  can be disabled via Settings.
- `StatTabs.svelte` uses flexible sizing so the panel fills its side.

