import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('RunMap component', () => {
  test('contains room button markup', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/RunMap.svelte'), 'utf8');
    expect(content).toContain('room-');
  });
});
