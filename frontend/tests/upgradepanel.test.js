import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('UpgradePanel component', () => {
  test('contains upgrade UI', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/UpgradePanel.svelte'), 'utf8');
    expect(content).toContain('data-testid="upgrade-panel"');
    expect(content).toContain('Upgrade Level');
    expect(content).toContain('Cost: 20×4★ or 100×3★ or 500×2★ or 1000×1★');
    expect(content).toContain('button');
  });
});
