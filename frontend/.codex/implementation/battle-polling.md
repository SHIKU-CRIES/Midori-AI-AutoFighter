# Battle polling

The `pollBattle` routine in `routes/+page.svelte` continuously polls the backend
for combat snapshots. It now tracks consecutive polls where combat has ended but
no rewards or completion flags have arrived. After roughly three seconds of
such stalled polling, the function stops the battle, records an error on the
snapshot, and logs a warning so the reward overlay or reset flow can proceed.

If a snapshot includes an `error` field, polling halts immediately and the
error state is surfaced without waiting for combat-over indicators.

Snapshots reporting `result: 'defeat'` are treated as complete even if an
`ended` flag is missing. The poller stops immediately and the defeat overlay
is shown.

Network failures now cause `handleRunEnd` when the backend reports the run has
ended. `pollBattle` watches for thrown errors whose message contains
"run ended" or whose status code is `404` and stops polling without queuing
another cycle. This prevents repeated error overlays once a run is gone.

Additionally, ending a run from Settings now immediately sets a global
`window.afHaltSync = true` flag and clears timers to prevent any further
`snapshot` polls during teardown. The same flag is set again in
`handleRunEnd()` before clearing run state and returning home.

When a battle completes with no rewards or choices (no cards/relics/loot) and
the backend marks `awaiting_next = true`, the UI now auto‑advances to the next
room without requiring the rewards overlay.
