// IMPORTANT: Do not guard import.meta.glob with typeof checks.
// Vite statically analyzes these calls to inline the module map.
const cardModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/cards/*/*.png', {
      eager: true,
      as: 'url'
    })
  )
);
const relicModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/relics/*/*.png', {
      eager: true,
      as: 'url'
    })
  )
);
const itemModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/items/*/*.png', {
      eager: true,
      as: 'url'
    })
  )
);

function normalizeUrl(src) {
  if (!src) return '';
  if (
    typeof src === 'string' &&
    (src.startsWith('http') || src.startsWith('blob:') || src.startsWith('data:') || src.startsWith('/'))
  ) {
    return src;
  }
  return new URL(src, import.meta.url).href;
}

function prepare(mods, fallback, useFolder = false) {
  const assets = {};
  const list = [];
  for (const path in mods) {
    const parts = path.split('/');
    const file = parts.pop().replace('.png', '');
    const folder = parts.pop();
    const name = useFolder ? `${folder}/${file}` : file;
    const href = normalizeUrl(mods[path]);
    assets[name] = href;
    list.push(href);
  }
  assets._all = list;
  assets._fallback = fallback || list[0] || '';
  return assets;
}

// Prefer gray default background art for missing card images
const defaultCardFallback = new URL(
  './assets/cards/gray/bg_attack_default_gray2.png',
  import.meta.url
).href;
const defaultRelicFallback = new URL(
  './assets/relics/fallback/placeholder.png',
  import.meta.url
).href;
const defaultItemFallback = new URL(
  './assets/items/generic/generic1.png',
  import.meta.url
).href;

export const cardArt = prepare(cardModules, defaultCardFallback, true);
export const relicArt = prepare(relicModules, defaultRelicFallback, true);
export const itemArt = prepare(itemModules, defaultItemFallback);

// Optional glyph background art drop-ins:
// Place files at:
//  - ./assets/cards/Art/<id>.png
//  - ./assets/relics/Art/<id>.png
// where <id> can be exact id (e.g., `pocket_manual.png`) or a compacted
// variant (e.g., `pocketmanual.png`). We match both id and name variants.
const cardGlyphModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/cards/Art/*.png', {
      eager: true,
      as: 'url'
    })
  )
);
const relicGlyphModules = Object.fromEntries(
  Object.entries(
    import.meta.glob('./assets/relics/Art/*.png', {
      eager: true,
      as: 'url'
    })
  )
);

function prepareGlyph(mods) {
  const map = {};
  for (const path in mods) {
    const file = path.split('/').pop().replace('.png', '');
    const href = normalizeUrl(mods[path]);
    // Use compacted keys only: lowercase alphanumerics, no spaces, no '_' or '-'
    const compact = file.toLowerCase().replace(/[^a-z0-9]/g, '');
    map[compact] = href;
  }
  return map;
}

const cardGlyphArt = prepareGlyph(cardGlyphModules);
const relicGlyphArt = prepareGlyph(relicGlyphModules);

function candidateKeys(entry) {
  const id = String(entry?.id || '').toLowerCase();
  const name = String(entry?.name || '').toLowerCase();
  const keys = [];
  if (id) keys.push(id.replace(/[^a-z0-9]/g, ''));
  if (name) keys.push(name.replace(/[^a-z0-9]/g, ''));
  return keys.filter(Boolean);
}

export function getGlyphArt(type, entry) {
  const art = type === 'card' ? cardGlyphArt : type === 'relic' ? relicGlyphArt : {};
  const keys = candidateKeys(entry);
  for (const k of keys) {
    if (art[k]) return art[k];
  }
  // Dev-only debug to help diagnose drop-in naming mismatches
  try {
    if (import.meta?.env?.DEV && typeof window !== 'undefined' && keys?.length) {
       
      console.debug('[glyphArt] no match', { type, id: entry?.id, name: entry?.name, keys });
    }
  } catch {}
  return '';
}

export function getRewardArt(type, id) {
  const lookup = type === 'card' ? cardArt : type === 'relic' ? relicArt : itemArt;
  return lookup[id] || lookup._fallback || '';
}

export function randomCardArt() {
  const list = cardArt._all || [];
  if (!list.length) {
    return cardArt._fallback || '';
  }
  const idx = Math.floor(Math.random() * list.length);
  return list[idx];
}
