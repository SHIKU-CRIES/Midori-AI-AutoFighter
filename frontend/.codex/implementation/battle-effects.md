# Battle Status & Ambient Effects

`+page.svelte` normalizes battle snapshots so each fighter carries
`passives`, `dots`, and `hots` as arrays of objects. Each effect object
includes an `id`, optional `name`, `stacks`, `turns`, and `source` along
with `damage` or `healing` values. `StatusIcons.svelte` and
`FighterPortrait.svelte` consume these arrays to render icons with stack
counts and tooltips showing effect details.

## Stained-Glass Palette

Effect indicators and bar graphs should reflect the project's stained-glass
aesthetic. Use vibrant, glass-like hues for these elements, drawing inspiration
from the element palette returned by `getElementBarColor` in
`frontend/src/lib/BattleReview.svelte`.

## Enrage Indicator Redesign

The previous blue/red full‑screen flashing during enrage has been replaced
with an ambient orbs effect implemented in `battle/EnrageIndicator.svelte`:

- Orbs gently drift and hue‑shift across the battlefield while combat is
  active and fade out smoothly once rewards appear (2–3s despawn).
- The indicator is now driven by `active` (combat state) rather than a binary
  enrage flag to avoid abrupt start/stop artifacts.
- Reduced Motion is respected: animations are disabled and a calm static
  ambience remains visible.

## Animation Pipeline

`BattleEffects.svelte` is currently disabled (no‑op) behind an internal
feature flag while we stabilize the runtime integration. When enabled, it
wraps the `@zaniar/effekseer-webgl-wasm` runtime. It creates a full-screen
canvas, initializes the WebGL context, and loads `.efkefc` files from
`src/lib/assets/effects`. `BattleView.svelte`
watches incoming battle log lines, maps keywords like `damage`, `burn`,
`poison`, and `heal` to effect names, and passes the result to the
component so the matching animation plays. `vite.config.js` copies the
`effekseer.wasm` runtime and marks `.efkefc` files as static assets so the
player can fetch them at runtime.
