import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('StatTabs editor persistence', () => {
  const content = readFileSync(join(import.meta.dir, '../src/lib/components/StatTabs.svelte'), 'utf8');

  test('stores editor values by character id', () => {
    expect(content).toContain('context="module"');
    expect(content).toMatch(/editorConfigs\s*=\s*new Map/);
    expect(content).toContain('editorConfigs.set(previewId, { ...editorVals });');
  });

  test('restores cached values when switching', () => {
    expect(content).toContain('const cached = editorConfigs.get(previewChar.id)');
  });

  test('shows global buff note after Regain row', () => {
    expect(content).toContain('export let userBuffPercent = 0');
    expect(content).toContain('Global Buff: +{userBuffPercent}%');
    const regainIndex = content.indexOf('<div><span>Regain</span>');
    const buffIndex = content.indexOf('Global Buff: +{userBuffPercent}%');
    expect(regainIndex).toBeLessThan(buffIndex);
  });
});
