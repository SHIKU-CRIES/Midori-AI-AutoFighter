// viewportState.js
// Helper utilities for GameViewport including settings init,
// room metadata helpers, and background music control.
import { loadSettings } from './settingsStorage.js';
import { getPlayers } from './api.js';
import { getRandomMusicTrack } from './music.js';

export async function loadInitialState() {
  const saved = loadSettings();
  const settings = {
    sfxVolume: saved.sfxVolume ?? 50,
    musicVolume: saved.musicVolume ?? 50,
    voiceVolume: saved.voiceVolume ?? 50,
    framerate: saved.framerate !== undefined ? Number(saved.framerate) : 60,
    autocraft: saved.autocraft ?? false,
    reducedMotion: saved.reducedMotion ?? false,
  };
  let roster = [];
  try {
    const data = await getPlayers();
    function resolveElement(p) {
      let e = p?.element;
      if (e && typeof e !== 'string') e = e.id || e.name;
      return e && !/generic/i.test(String(e)) ? e : 'Generic';
    }
    roster = data.players.map(p => ({ id: p.id, element: resolveElement(p) }));
  } catch {
    roster = [];
  }
  return { settings, roster };
}

export function mapSelectedParty(roster, selected) {
  return selected.map(id => {
    const info = roster.find(r => r.id === id);
    return { id, element: info?.element || 'Generic' };
  });
}

export function roomLabel(type) {
  switch (String(type || '')) {
    case 'battle-weak':
      return 'Weak Battle';
    case 'battle-normal':
      return 'Normal Battle';
    case 'battle-boss-floor':
      return 'Floor Boss';
    case 'shop':
      return 'Shop';
    case 'rest':
      return 'Rest';
    case 'start':
      return 'Start';
    default:
      if (!type) return 'Battle';
      return String(type).replace(/\b\w/g, c => c.toUpperCase()).replaceAll('-', ' ');
  }
}

export function roomInfo(mapRooms, currentIndex, currentRoomType, roomData) {
  return {
    roomNumber: mapRooms?.[currentIndex]?.index ?? currentIndex ?? 0,
    floorNumber: mapRooms?.[currentIndex]?.floor ?? 1,
    currentType: currentRoomType || roomData?.current_room || '',
    nextType: mapRooms?.[currentIndex + 1]?.room_type || (roomData?.next_room ?? ''),
  };
}

export function rewardOpen(roomData, battleActive) {
  const isBattle = roomData && (roomData.result === 'battle' || roomData.result === 'boss');
  return !!(isBattle && !battleActive);
}

let gameAudio;
let volumeTimer;

export function startGameMusic(volume) {
  stopGameMusic();
  const src = getRandomMusicTrack();
  if (!src) return;
  gameAudio = new Audio(src);
  applyMusicVolume(volume);
  gameAudio.addEventListener('ended', () => startGameMusic(volume));
  gameAudio.play().catch(() => {});
  volumeTimer = setInterval(() => {
    applyMusicVolume(volume);
  }, 500);
}

export function applyMusicVolume(volume) {
  if (gameAudio) {
    gameAudio.volume = volume / 100;
  }
}

export function stopGameMusic() {
  if (volumeTimer) {
    clearInterval(volumeTimer);
    volumeTimer = null;
  }
  if (gameAudio) {
    gameAudio.pause();
    gameAudio = null;
  }
}
