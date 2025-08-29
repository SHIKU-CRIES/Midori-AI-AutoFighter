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

export function rewardOpen(roomData, _battleActive) {
  if (!roomData) return false;
  const hasCards = (roomData?.card_choices?.length || 0) > 0;
  const hasRelics = (roomData?.relic_choices?.length || 0) > 0;
  const hasLootItems = (roomData?.loot?.items?.length || 0) > 0;
  const hasLootGold = (roomData?.loot?.gold || 0) > 0;
  return Boolean(hasCards || hasRelics || hasLootItems || hasLootGold);
}

let gameAudio;
let currentMusicVolume = 50;

export function startGameMusic(volume) {
  if (typeof volume === 'number') currentMusicVolume = volume;
  stopGameMusic();
  const src = getRandomMusicTrack();
  if (!src) return;
  gameAudio = new Audio(src);
  // Always use the latest requested volume
  applyMusicVolume(currentMusicVolume);
  gameAudio.addEventListener('ended', () => startGameMusic());
  gameAudio.play().catch(() => {});
}

export function applyMusicVolume(volume) {
  currentMusicVolume = typeof volume === 'number' ? volume : currentMusicVolume;
  if (gameAudio) {
    gameAudio.volume = currentMusicVolume / 100;
  }
}

export function stopGameMusic() {
  if (gameAudio) {
    try { gameAudio.pause(); } catch {}
    gameAudio = null;
  }
}

export function resumeGameMusic() {
  // Try to start or resume playback after a user gesture
  try {
    if (gameAudio) {
      if (gameAudio.paused) {
        gameAudio.volume = currentMusicVolume / 100;
        gameAudio.play().catch(() => {});
      }
    } else {
      startGameMusic();
    }
  } catch {}
}
