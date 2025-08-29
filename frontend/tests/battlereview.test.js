import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

const review = readFileSync(join(import.meta.dir, '../src/lib/BattleReview.svelte'), 'utf8');

describe('BattleReview component', () => {
  test('renders party and foe sections', () => {
    expect(review).toContain('{#each party as member}');
    expect(review).toContain('{#each foes as foe}');
  });

  test('includes reward components', () => {
    expect(review).toContain('RewardCard');
    expect(review).toContain('CurioChoice');
  });

  test('uses colored damage bars', () => {
    expect(review).toContain('class="bars"');
    expect(review).toContain('getElementColor');
  });
});
