// Music loader for background tracks
// Tracks are provided by the lead developer in ./assets/music

const musicModules = import.meta.glob('../assets/music/**/*.{mp3,ogg,wav}', {
  eager: true,
  import: 'default',
  query: '?url'
});

// Character-specific library (supports any top-level folder except 'fallback')
const characterLibrary = {};
// Fallback library used when a character has no music (or is not explicitly supported)
const fallbackLibrary = {};

for (const [path, url] of Object.entries(musicModules)) {
  const parts = path.split('/');
  const character = parts[3];
  const category = parts[4] ?? 'other';
  if (!character || !category) continue;

  const key = character.toLowerCase();
  if (key === 'fallback') {
    fallbackLibrary[category] ??= [];
    fallbackLibrary[category].push(url);
  } else {
    characterLibrary[key] ??= {};
    characterLibrary[key][category] ??= [];
    characterLibrary[key][category].push(url);
  }
}

export function shuffle(array) {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function getMusicTracks() {
  // Return all fallback tracks across categories as a flat list
  return Object.values(fallbackLibrary).flat();
}

export function getCharacterPlaylist(charName, category = 'normal') {
  const key = String(charName || '').toLowerCase();
  const charMusic = characterLibrary[key] ?? {};
  const tracks = charMusic[category] ?? [];
  // Return in indexed order; caller decides if and when to shuffle
  return [...tracks];
}

export function getRandomMusicTrack(charName, category = 'normal') {
  const tracks = charName ? getCharacterPlaylist(charName, category) : getMusicTracks();
  if (tracks.length === 0) return '';
  const index = Math.floor(Math.random() * tracks.length);
  return tracks[index];
}

export function getFallbackPlaylist(category = 'normal') {
  const tracks = fallbackLibrary[category] ?? [];
  // Return in indexed order; caller decides if and when to shuffle
  return [...tracks];
}

export { characterLibrary };
