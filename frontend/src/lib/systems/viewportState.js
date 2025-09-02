// viewportState.js
// Helper utilities for GameViewport including settings init,
// room metadata helpers, and background music control.
import { loadSettings } from './settingsStorage.js';
import { getPlayers } from './api.js';
import {
  getCharacterPlaylist,
  getMusicTracks,
  getRandomMusicTrack,
} from './music.js';

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
  const cur = mapRooms?.[currentIndex] || null;
  const nxt = mapRooms?.[currentIndex + 1] || null;
  return {
    pressure: cur?.pressure ?? roomData?.pressure ?? 0,
    floorNumber: cur?.floor ?? 1,
    roomNumber: cur?.index ?? currentIndex ?? 0,
    currentType: currentRoomType || roomData?.current_room || '',
    nextType: nxt?.room_type || (roomData?.next_room ?? ''),
  };
}

export function rewardOpen(roomData, _battleActive) {
  if (!roomData) return false;
  const hasCards = (roomData?.card_choices?.length || 0) > 0;
  const hasRelics = (roomData?.relic_choices?.length || 0) > 0;
  // Only open the reward overlay for selectable choices (cards/relics).
  // Loot items/gold are displayed via floating messages, not as a blocking popup.
  return Boolean(hasCards || hasRelics);
}

export function selectBattleMusic({ roomType, party = [], foes = [] }) {
  const type = String(roomType || '');
  const category =
    type === 'battle-weak'
      ? 'weak'
      : type === 'battle-boss-floor'
        ? 'boss'
        : 'normal';

  if (type === 'battle-boss-floor') {
    const boss = foes?.[0];
    const name = typeof boss === 'string' ? boss : boss?.id || boss?.name;
    const playlist = getCharacterPlaylist(String(name || '').toLowerCase(), 'boss');
    if (playlist.length) return playlist;
    return getMusicTracks();
  }

  const candidates = [];

  function addCandidate(entity, weight = 1) {
    const name = typeof entity === 'string' ? entity : entity?.id || entity?.name;
    if (!name) return;
    const list = getCharacterPlaylist(String(name).toLowerCase(), category);
    if (list.length) candidates.push({ list, weight });
  }

  party.forEach(p => addCandidate(p));
  foes.forEach(f => {
    const id = typeof f === 'string' ? f : f?.id || f?.name;
    const weight = String(id).toLowerCase() === 'luna' ? 3 : 1;
    addCandidate(id, weight);
  });

  if (candidates.length === 0) {
    const generic = getCharacterPlaylist('generic', category);
    return generic.length ? generic : getMusicTracks();
  }

  const total = candidates.reduce((sum, c) => sum + c.weight, 0);
  let roll = Math.random() * total;
  for (const c of candidates) {
    roll -= c.weight;
    if (roll <= 0) return c.list;
  }
  return candidates[0].list;
}

let gameAudio;
let currentMusicVolume = 50;
let currentPlaylist = [];
let playlistIndex = 0;
let playlistLoop = true;

function playNextTrack() {
  const src =
    currentPlaylist.length > 0
      ? currentPlaylist[playlistIndex]
      : getRandomMusicTrack();
  if (!src) return;
  gameAudio = new Audio(src);
  applyMusicVolume(currentMusicVolume);
  gameAudio.addEventListener('ended', () => {
    if (currentPlaylist.length > 0) {
      playlistIndex += 1;
      if (playlistIndex >= currentPlaylist.length) {
        if (playlistLoop) {
          playlistIndex = 0;
        } else {
          currentPlaylist = [];
        }
      }
    }
    playNextTrack();
  });
  gameAudio.play().catch(() => {});
}

export function startGameMusic(volume, playlist = [], loop = true) {
  if (typeof volume === 'number') currentMusicVolume = volume;
  stopGameMusic();
  if (Array.isArray(playlist) && playlist.length > 0) {
    currentPlaylist = playlist;
    playlistIndex = 0;
    playlistLoop = loop;
  } else {
    currentPlaylist = [];
  }
  playNextTrack();
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
  try {
    if (gameAudio) {
      if (gameAudio.paused) {
        gameAudio.volume = currentMusicVolume / 100;
        gameAudio.play().catch(() => {});
      }
    } else {
      startGameMusic(currentMusicVolume, currentPlaylist, playlistLoop);
    }
  } catch {}
}
