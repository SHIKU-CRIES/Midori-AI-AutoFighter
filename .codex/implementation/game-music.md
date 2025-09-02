# Game Music

`viewportState.js` provides helpers to play background music.
`GameViewport.svelte` calls these helpers on mount to start a random
track from `src/lib/assets/music` and applies the saved
`musicVolume` about every 0.5 s so changes take effect quickly.

## Asset discovery

`src/lib/systems/music.js` uses `import.meta.glob('../assets/music/**/*.{mp3,ogg,wav}', { eager: true })`
to eagerly load every audio file under `src/lib/assets/music`. The search is recursive,
so adding new tracks anywhere in that tree automatically includes them in the game
without further code changes.

### Character and category naming

Files follow the structure `assets/music/<character>/<category>/<file>`. Character
folders use lowercase identifiers matching player or foe names. Each character may
contain category subfolders such as `normal`, `weak`, `boss`, or `menu`; if the
category is omitted the file falls under `other`.

## Boss overrides and weights

`selectBattleMusic()` picks a playlist for fights. In `battle-boss-floor` rooms the
first foe's `boss` playlist overrides and plays if present, otherwise the global
library is used. For regular battles the party and foes contribute their playlists
and a weighted roll chooses one. Foes named `Luna` receive a weight of 3 while all
others use 1, giving Luna's themes a higher chance to play.

## Shuffling and playback

`startGameMusic()` shuffles the selected playlist with a Fisher–Yates algorithm and
loops it. When the playlist ends it reshuffles before replaying; if no playlist is
active a random track is chosen from the full library. Because assets are discovered
recursively, any additional files dropped into `assets/music` are picked up and
participate in this shuffle automatically.

Headless environments may not support audio playback; tests rely on Bun's no-op
`Audio` implementation so CI runs without sound hardware.
