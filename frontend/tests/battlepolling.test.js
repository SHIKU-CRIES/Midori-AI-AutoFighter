import { readFileSync } from 'fs';
import { join } from 'path';
import { describe, test, expect, mock } from 'bun:test';

describe('battle polling', () => {
  test('stops on error snapshots', () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    expect(content).toContain('if (snap?.error)');
    expect(content).toContain('battleActive = false');
  });

  test('halts on 404 without overlay spam', async () => {
    let overlayCalls = 0;
    mock.module('../src/lib/OverlayController.js', () => ({
      openOverlay: () => { overlayCalls += 1; },
      backOverlay: () => {},
      homeOverlay: () => {}
    }));

    const { roomAction } = await import('../src/lib/runApi.js');
    global.fetch = mock(async () => ({ ok: false, status: 404, json: async () => ({ message: 'run ended' }) }));

    const content = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    const match = content.match(/async function pollBattle\(\)[\s\S]*?\n  }/);
    const fnSource = match ? match[0] : '';

    let setTimeoutCalled = false;
    const ctx = {
      battleActive: true,
      haltSync: false,
      runId: 'abc',
      roomAction,
      handleRunEnd: () => { ctx.battleActive = false; ctx.runId = ''; },
      setTimeout: () => { setTimeoutCalled = true; },
      mapStatuses: (x) => x,
      hasRewards: () => false,
      STALL_TICKS: 180,
      stalledTicks: 0,
      dev: false,
      browser: true,
      battleTimer: null
    };

    const poll = new Function('ctx', `with (ctx) { ${fnSource}; return pollBattle; }`)(ctx);
    await poll();

    expect(ctx.battleActive).toBe(false);
    expect(ctx.runId).toBe('');
    expect(setTimeoutCalled).toBe(false);
    expect(overlayCalls).toBe(0);
  });
});
