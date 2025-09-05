import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('UpgradePanel component', () => {
  test('contains new upgrade UI hooks', () => {
    // Note: file path reflects the component location in src/lib/components
    const content = readFileSync(join(import.meta.dir, '../src/lib/components/UpgradePanel.svelte'), 'utf8');
    expect(content).toContain('data-testid="upgrade-panel"');
    expect(content).toContain('Convert items'); // section label
    expect(content).toContain('Convert to Points'); // unified button text
    expect(content).toContain('Spend points'); // stat spend UI
  });
});
