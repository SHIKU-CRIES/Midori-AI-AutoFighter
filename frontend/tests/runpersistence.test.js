import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Run persistence', () => {
  const page = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
  const state = readFileSync(join(import.meta.dir, '../src/lib/runState.js'), 'utf8');

  test('page uses runState helpers', () => {
    expect(page).toContain('loadRunState');
    expect(page).toContain('saveRunState(');
  });

  test('runState reads and writes localStorage', () => {
    expect(state).toContain('localStorage.getItem');
    expect(state).toContain('localStorage.setItem');
    expect(state).toContain('STORAGE_KEY');
  });
});
