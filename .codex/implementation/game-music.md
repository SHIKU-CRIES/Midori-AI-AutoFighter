# Game Music

`viewportState.js` provides helpers to play background music. 
`GameViewport.svelte` calls these helpers on mount to start a random
track from `src/lib/assets/music` and applies the saved 
`musicVolume` about every 0.5 s so changes take effect quickly.

Headless environments may not support audio playback; tests rely on Bun's no-op `Audio`
implementation so CI runs without sound hardware.
