import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('PartyPicker component', () => {
  test('uses dynamic assets and player fetch', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/PartyPicker.svelte'), 'utf8');
    expect(content).toContain('import.meta.glob');
    expect(content).toContain('getPlayers');
    expect(content).toContain('mask-image');
  });
});
