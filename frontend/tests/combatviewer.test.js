import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

const combatViewer = readFileSync(join(import.meta.dir, '../src/lib/components/CombatViewer.svelte'), 'utf8');

describe('CombatViewer passive display modes', () => {
  test('renders spinner display', () => {
    expect(combatViewer).toContain("effect.display === 'spinner'");
    expect(combatViewer).toContain('<Spinner');
  });

  test('renders pips with numeric fallback', () => {
    expect(combatViewer).toContain("effect.display === 'pips'");
    expect(combatViewer).toContain('effect.stacks <= 5');
    expect(combatViewer).toContain('pip-count');
  });

  test('renders numeric count display', () => {
    expect(combatViewer).toContain("effect.display === 'number'");
  });
});
