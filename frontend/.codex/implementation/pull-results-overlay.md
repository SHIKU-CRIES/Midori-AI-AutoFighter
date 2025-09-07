# Pull Results Overlay

`src/lib/components/PullResultsOverlay.svelte` displays gacha pull results.
It accepts a `results` array and uses `CurioChoice.svelte` to render each
entry. Results are queued and revealed one at a time with a simple slide/fade
animation. After all items appear a Done button lets the player close the
overlay.
