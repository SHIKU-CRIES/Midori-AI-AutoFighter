import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('CharacterEditor component', () => {
  test('contains editor fields', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/components/CharacterEditor.svelte'), 'utf8');
    expect(content).toContain('data-testid="character-editor"');
    expect(content).toContain('label for="pronouns"');
    expect(content).toContain('label for="damage"');
    expect(content).toContain('damageType');
    expect(content).toContain('Crit Rate');
    expect(content).toContain('Crit Damage');
  });
});
