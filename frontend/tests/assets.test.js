import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

function pngSize(path) {
  const buf = readFileSync(path);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

describe('asset placeholders', () => {
  test('item icons exist for each damage type', () => {
    const types = ['dark', 'fire', 'ice', 'light', 'lightning', 'wind', 'generic'];
    for (const t of types) {
      const file = join(import.meta.dir, `../src/lib/assets/items/${t}/generic1.png`);
      const { width, height } = pngSize(file);
      expect(width).toBe(24);
      expect(height).toBe(24);
    }
  });

  test('relic and card placeholders cover all star ranks', () => {
    const ranks = ['1star', '2star', '3star', '4star', '5star', 'fallback'];
    for (const r of ranks) {
      const relic = join(import.meta.dir, `../src/lib/assets/relics/${r}/placeholder.png`);
      const card = join(import.meta.dir, `../src/lib/assets/cards/${r}/placeholder.png`);
      const relicSize = pngSize(relic);
      const cardSize = pngSize(card);
      expect(relicSize).toEqual({ width: 24, height: 24 });
      expect(cardSize).toEqual({ width: 24, height: 24 });
    }
  });
});
