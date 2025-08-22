# Battle Status Mapping

`+page.svelte` normalizes battle snapshots so each fighter carries
`passives`, `dots`, and `hots` as arrays of objects. Each effect object
includes an `id`, optional `name`, `stacks`, `turns`, and `source` along
with `damage` or `healing` values. `StatusIcons.svelte` and
`FighterPortrait.svelte` consume these arrays to render icons with stack
counts and tooltips showing effect details.
