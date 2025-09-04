import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Party persistence', () => {
  test('restores party from backend on load', () => {
    const content = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    expect(content).toContain('selectedParty = data.party || selectedParty');
  });

  test('applies backend party to selection when entering room', () => {
    const content = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    expect(content).toContain('selectedParty = data.party.map((p) => p.id)');
  });

  test('saves updated party to backend', () => {
    const content = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    expect(content).toContain('updateParty(selectedParty)');
  });
});
