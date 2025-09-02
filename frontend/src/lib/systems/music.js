// Music loader for background tracks
// Tracks are provided by the lead developer in ./assets/music

const musicModules = import.meta.glob('../assets/music/**/*.{mp3,ogg,wav}', {
  eager: true,
  import: 'default',
  query: '?url'
});

const musicLibrary = {};

for (const [path, url] of Object.entries(musicModules)) {
  const parts = path.split('/');
  const character = parts[3];
  const category = parts[4] ?? 'other';

  if (!character || !category) continue;

  musicLibrary[character] ??= {};
  musicLibrary[character][category] ??= [];
  musicLibrary[character][category].push(url);
}

function shuffle(array) {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function getMusicTracks() {
  return Object.values(musicModules);
}

export function getCharacterPlaylist(charName, category = 'normal') {
  const charMusic = musicLibrary[charName] ?? {};
  const tracks = charMusic[category] ?? [];
  return shuffle(tracks);
}

export function getRandomMusicTrack(charName, category = 'normal') {
  const tracks = charName ? getCharacterPlaylist(charName, category) : getMusicTracks();
  if (tracks.length === 0) return '';
  const index = Math.floor(Math.random() * tracks.length);
  return tracks[index];
}

export { musicLibrary };
