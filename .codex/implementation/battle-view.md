# Battle View

`BattleView.svelte` renders turn-based encounters inside `MenuPanel` and now
acts primarily as a coordinator. It draws a random backdrop from the shared
`assetLoader` and displays the party and foes in opposing columns, with the
party fixed to the left and foes to the right using explicit flex order.

Visual pieces have been split into small subcomponents under
`src/lib/battle/`:

- `FighterPortrait.svelte` – portrait, HP bar, element chip (with
  square dark backdrop and fading outer glow) and embedded
  `StatusIcons`. Passive stack pips render as lucide icons and tint
  to the element color when filled.
- `StatusIcons.svelte` – collapses duplicate HoT/DoT names into single icons
  with stack counts.
- `EnrageIndicator.svelte` – pulsing red/blue overlay when the backend reports
  `enrage.active`.
- `BattleLog.svelte` – lightweight scrollable list fed with log messages from
  snapshots.

Each combatant lists HP, ATK, DEF, mitigation, and crit rate beside their
portrait, mirroring the same order for party and foes. Shared fallback art
appears when portraits are missing, and the layout scales down on small screens
so both the bars and numeric values remain readable.

Snapshots from the backend are polled once per frame-rate tick rather than on a
fixed interval and the polling delay honors 30/60/120 fps settings without a
50 ms floor. Each request dispatches events with the round-trip time so
`NavBar` shows a stained-glass status panel with a
spinner while updates are in flight. Incoming party and foe arrays are compared
to the previous snapshot to avoid unnecessary re-renders.

## Testing
- `bun test frontend/tests/battleview.test.js`
