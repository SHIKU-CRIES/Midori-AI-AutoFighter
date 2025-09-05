import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

function buildHandler() {
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
  return new Function(
    'runId',
    'endRun',
    'endAllRuns',
    'getActiveRuns',
    'dispatch',
    `let endRunStatus = ''; let endingRun = false; return (async () => {${body} return endRunStatus;})();`
  );
}

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

  test('reports success when targeted run ends', async () => {
    const handler = buildHandler();
    const calls = [];
    const dispatches = [];
    const status = await handler(
      'abc',
      async () => { calls.push('endRun'); },
      () => { calls.push('endAllRuns'); },
      () => ({ runs: [] }),
      () => dispatches.push('endRun')
    );
    expect(calls).toEqual(['endRun']);
    expect(dispatches).toEqual(['endRun']);
    expect(status).toBe('Run ended');
  });

  test('falls back to endAllRuns when endRun fails', async () => {
    const handler = buildHandler();
    const calls = [];
    const dispatches = [];
    const status = await handler(
      'abc',
      async () => { calls.push('endRun'); throw new Error('fail'); },
      () => { calls.push('endAllRuns'); },
      () => ({ runs: [] }),
      () => dispatches.push('endRun')
    );
    expect(calls).toEqual(['endRun', 'endAllRuns']);
    expect(dispatches).toEqual(['endRun']);
    expect(status).toBe('Run force-ended');
  });

  test('uses endAllRuns when runId is missing', async () => {
    const handler = buildHandler();
    const calls = [];
    const dispatches = [];
    const status = await handler(
      '',
      () => { calls.push('endRun'); },
      () => { calls.push('endAllRuns'); },
      () => ({ runs: [] }),
      () => dispatches.push('endRun')
    );
    expect(calls).toEqual(['endAllRuns']);
    expect(dispatches).toEqual(['endRun']);
    expect(status).toBe('Run force-ended');
  });
});
