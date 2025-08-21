// Enhanced asset loader for characters, backgrounds, and damage types

import { Flame, Snowflake, Zap, Sun, Moon, Wind, Circle } from 'lucide-svelte';

// Safely normalize a URL string coming from Vite globs
function normalizeUrl(src) {
  if (!src) return '';
  // If Vite already gave us an absolute or root-relative path, use it as-is.
  if (
    typeof src === 'string' &&
    (src.startsWith('http') || src.startsWith('blob:') || src.startsWith('data:') || src.startsWith('/'))
  ) {
    return src;
  }
  return new URL(src, import.meta.url).href;
}

// Load all character images (including folders and fallbacks)
// Note: do NOT guard import.meta.glob with typeof checks — Vite must
// statically analyze these calls to inline the module map at build time.
const characterModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/characters/**/*.png', {
      eager: true,
      as: 'url'
    })
  ).map(([p, src]) => [p, normalizeUrl(src)])
);

const fallbackModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/characters/fallbacks/*.png', {
      eager: true,
      as: 'url'
    })
  ).map(([p, src]) => [p, normalizeUrl(src)])
);

const backgroundModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/backgrounds/*.png', {
      eager: true,
      as: 'url'
    })
  ).map(([p, src]) => [p, normalizeUrl(src)])
);

// Load DoT icons by element folder (e.g., ./assets/dots/fire/*.png)
const dotModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/dots/*/*.png', {
      eager: true,
      as: 'url'
    })
  ).map(([p, src]) => [p, normalizeUrl(src)])
);

const ELEMENT_ICONS = {
  fire: Flame,
  ice: Snowflake,
  lightning: Zap,
  light: Sun,
  dark: Moon,
  wind: Wind,
  generic: Circle
};

const ELEMENT_COLORS = {
  fire: '#e25822',
  ice: '#82caff',
  lightning: '#ffd700',
  light: '#ffff99',
  dark: '#8a2be2',
  wind: '#7fff7f',
  generic: '#cccccc'
};

// Parse character assets into organized structure
const characterAssets = {};
const fallbackAssets = Object.values(fallbackModules);
const backgroundAssets = Object.values(backgroundModules);
const defaultFallback = normalizeUrl('./assets/midoriai-logo.png');
const DOT_DEFAULT = normalizeUrl('./assets/dots/generic/generic1.png');

// Organize character assets by character ID (folder or single file)
Object.keys(characterModules).forEach(p => {
  const match = p.match(/\.\/assets\/characters\/(.+?)\/(.+?)\.png$/) ||
                p.match(/\.\/assets\/characters\/(.+?)\.png$/);
  
  if (match) {
    const [, charId, fileName] = match;
    const actualCharId = fileName ? charId : charId.replace('.png', '');
    
    if (!characterAssets[actualCharId]) {
      characterAssets[actualCharId] = [];
    }

    // Skip fallbacks folder
    if (actualCharId !== 'fallbacks') {
      characterAssets[actualCharId].push(characterModules[p]);
    }
  }
});

// Seeded random function for consistent hourly backgrounds
function seededRandom(seed) {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

// Get current hour seed (changes every hour)
function getHourSeed() {
  const now = new Date();
  return now.getFullYear() * 1000000 + 
         now.getMonth() * 10000 + 
         now.getDate() * 100 + 
         now.getHours();
}

// Get random image from character folder or fallback
export function getCharacterImage(characterId, _isPlayer = false) {
  // Stable selection per character so portraits don't flicker on re-render
  if (!characterId) return defaultFallback;
  const cached = characterImageCache.get(characterId);
  if (cached) return cached;

  // Dedicated images
  if (characterAssets[characterId] && characterAssets[characterId].length > 0) {
    const images = characterAssets[characterId];
    const idx = stringHashIndex(characterId, images.length);
    const chosen = images[idx];
    characterImageCache.set(characterId, chosen);
    return chosen;
  }

  // Fallback images (stable per id)
  if (fallbackAssets.length > 0) {
    const idx = stringHashIndex(characterId, fallbackAssets.length);
    const chosen = fallbackAssets[idx];
    characterImageCache.set(characterId, chosen);
    return chosen;
  }

  // Final fallback - repository logo
  characterImageCache.set(characterId, defaultFallback);
  return defaultFallback;
}

// Get background with hourly consistency
export function getHourlyBackground() {
  if (backgroundAssets.length === 0) return defaultFallback;
  
  const seed = getHourSeed();
  const randomIndex = Math.floor(seededRandom(seed) * backgroundAssets.length);
  return backgroundAssets[randomIndex];
}

// Get random background (for immediate random needs)
export function getRandomBackground() {
  if (backgroundAssets.length === 0) return defaultFallback;

  const randomIndex = Math.floor(Math.random() * backgroundAssets.length);
  return backgroundAssets[randomIndex];
}

// Get all available character IDs
export function getAvailableCharacterIds() {
  return Object.keys(characterAssets);
}

// Get random fallback image
export function getRandomFallback() {
  if (fallbackAssets.length === 0) return defaultFallback;

  const randomIndex = Math.floor(Math.random() * fallbackAssets.length);
  return fallbackAssets[randomIndex];
}

export function getElementIcon(element) {
  return ELEMENT_ICONS[(element || '').toLowerCase()] || Circle;
}

export function getElementColor(element) {
  return ELEMENT_COLORS[(element || '').toLowerCase()] || '#aaa';
}

// Build DoT assets map: { fire: [urls...], ice: [...], ... }
const dotAssets = (() => {
  const map = {
    fire: [],
    ice: [],
    lightning: [],
    light: [],
    dark: [],
    wind: [],
    generic: []
  };
  for (const [p, url] of Object.entries(dotModules)) {
    const m = p.match(/\.\/assets\/dots\/(\w+)\//);
    const key = (m?.[1] || 'generic').toLowerCase();
    if (!map[key]) map[key] = [];
    map[key].push(url);
  }
  return map;
})();

// Choose a DoT icon based on id text (e.g., "fire_dot", "blazing_torment")
// Falls back to generic if no themed match is found.
export function getDotImage(idOrName) {
  const key = String(idOrName || '').toLowerCase();
  const element =
    (key.includes('fire') && 'fire') ||
    (key.includes('ice') && 'ice') ||
    (key.includes('lightning') && 'lightning') ||
    // ensure 'lightning' check runs before 'light'
    (key.includes('light') && 'light') ||
    (key.includes('dark') && 'dark') ||
    (key.includes('wind') && 'wind') ||
    'generic';
  const list = dotAssets[element] || dotAssets.generic || [];
  if (list.length === 0) return DOT_DEFAULT || defaultFallback;
  const idx = stringHashIndex(key || element, list.length);
  return list[idx] || DOT_DEFAULT || defaultFallback;
}

// Export assets for debugging
export { characterAssets, fallbackAssets, backgroundAssets };

// Internal: cache and helpers for stable image selection
const characterImageCache = new Map();

function stringHashIndex(str, modulo) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i);
    h |= 0;
  }
  const idx = Math.abs(h) % Math.max(modulo, 1);
  return idx;
}

export function clearCharacterImageCache() {
  characterImageCache.clear();
}
