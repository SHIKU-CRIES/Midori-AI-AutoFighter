# Battle Music

Describes how the frontend selects playlists for combat.

## selectBattleMusic
`selectBattleMusic({ roomType, party, foes })` returns a playlist of music
tracks for the next room transition.

- **Boss rooms** (`roomType === 'battle-boss-floor'`)
  - Always returns the boss's `boss` playlist.
  - Playlist loops continuously.
- **Non-boss battles**
  - Collects playlists for every combatant present.
  - Each playlist is weighted equally, but Luna receives an extra weight when
    appearing as a foe.
  - A weighted roll decides which playlist to use.
- **Fallback**
  - When no character has music, generic library tracks are returned.

The chosen playlist is passed to `startGameMusic` which handles sequential
playback and looping.
