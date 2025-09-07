import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('InventoryPanel', () => {
  test('renders upgrade materials section', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/components/InventoryPanel.svelte'), 'utf8');
    expect(content).toContain('Upgrade Materials');
    expect(content).toContain('materials-grid');
  });
});
