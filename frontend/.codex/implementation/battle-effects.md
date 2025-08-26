# Battle Status Mapping

`+page.svelte` normalizes battle snapshots so each fighter carries
`passives`, `dots`, and `hots` as arrays of objects. Each effect object
includes an `id`, optional `name`, `stacks`, `turns`, and `source` along
with `damage` or `healing` values. `StatusIcons.svelte` and
`FighterPortrait.svelte` consume these arrays to render icons with stack
counts and tooltips showing effect details.

## Animation Pipeline

`BattleEffects.svelte` is currently disabled (no-op) behind an internal
feature flag while we stabilize the runtime integration. When enabled, it
wraps the `@zaniar/effekseer-webgl-wasm` runtime. It creates a full-screen
canvas, initializes the WebGL context, and loads `.efkefc` files from
`src/lib/assets/effects`. `BattleView.svelte`
watches incoming battle log lines, maps keywords like `damage`, `burn`,
`poison`, and `heal` to effect names, and passes the result to the
component so the matching animation plays. `vite.config.js` copies the
`effekseer.wasm` runtime and marks `.efkefc` files as static assets so the
player can fetch them at runtime.
