import { readFileSync } from 'fs';
import { join } from 'path';
import { describe, test, expect } from 'bun:test';

describe('battle polling', () => {
  test('stops on error snapshots', () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    expect(content).toContain('if (snap?.error)');
    expect(content).toContain('battleActive = false');
  });
});
