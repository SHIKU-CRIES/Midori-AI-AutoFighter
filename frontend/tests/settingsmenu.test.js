import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('SettingsMenu component', () => {
  test('renders tab icons and panels', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/components/SettingsMenu.svelte'), 'utf8');
    expect(content).toContain('class="tabs"');
    expect(content).toContain('<Volume2 />');
    expect(content).toContain('<Cog />');
    expect(content).toContain('<Brain />');
    expect(content).toContain('<Gamepad />');
    expect(content).toContain('SFX Volume');
    expect(content).toContain('Music Volume');
    expect(content).toContain('Voice Volume');
    expect(content).toContain('Wipe Save Data');
    expect(content).toContain('Backup Save Data');
    expect(content).toContain('Import Save Data');
    expect(content).toContain('End Run');
    expect(content).toContain('data-testid="wipe-status"');
    expect(content).toContain('data-testid="save-status"');
    expect(content).toContain('LRM Model');
    expect(content).toContain('Test Model');
    expect(content).toContain('backendFlavor');
    expect(content).toContain('{#if showLrm}');
    expect(content).toContain('if (showLrm)');
    expect(content).not.toContain('Save</button>');
    expect(content).not.toContain('alert(');
  });

  test('dispatches endRun even if API call fails', async () => {
    const source = readFileSync(join(import.meta.dir, '../src/lib/components/SettingsMenu.svelte'), 'utf8');
    const start = source.indexOf('async function handleEndRun');
    const brace = source.indexOf('{', start);
    let depth = 1;
    let i = brace + 1;
    while (depth > 0 && i < source.length) {
      if (source[i] === '{') depth++;
      else if (source[i] === '}') depth--;
      i++;
    }
    const body = source.slice(brace + 1, i - 1);
    let fired = false;
    const handler = new Function('runId', 'endRun', 'dispatch', `return (async () => {${body}})();`);
    await handler('abc', async () => { throw new Error('fail'); }, () => { fired = true; });
    expect(fired).toBe(true);
  });
});
