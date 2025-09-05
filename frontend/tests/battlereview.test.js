import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

const review = readFileSync(join(import.meta.dir, '../src/lib/components/BattleReview.svelte'), 'utf8');

describe('BattleReview component', () => {
  test('maps party and foe data', () => {
    expect(review).toContain('partyDisplay');
    expect(review).toContain('foesDisplay');
  });

  test('includes reward components', () => {
    expect(review).toContain('RewardCard');
    expect(review).toContain('CurioChoice');
  });

  test('uses icon column navigation', () => {
    expect(review).toContain('icon-column');
    expect(review).toContain('stats-panel');
  });

  test('foe tabs show rank when available', () => {
    expect(review).toMatch(/foe\.rank/);
    expect(review).toMatch(/\u2014/); // em dash between name and rank
  });
});
