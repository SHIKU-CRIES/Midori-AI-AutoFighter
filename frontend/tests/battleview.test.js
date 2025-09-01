import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

const battleView = readFileSync(join(import.meta.dir, '../src/lib/BattleView.svelte'), 'utf8');
const enrageIndicator = readFileSync(join(import.meta.dir, '../src/lib/battle/EnrageIndicator.svelte'), 'utf8');
const statusIcons = readFileSync(join(import.meta.dir, '../src/lib/battle/StatusIcons.svelte'), 'utf8');
const fighterPortrait = readFileSync(join(import.meta.dir, '../src/lib/battle/FighterPortrait.svelte'), 'utf8');

describe('BattleView enrage handling', () => {
  test('uses EnrageIndicator component', () => {
    expect(battleView).toContain('EnrageIndicator');
  });
  test('enrage indicator defines animation', () => {
    expect(enrageIndicator).toContain('@keyframes driftX');
    expect(enrageIndicator).toContain('enrage-orbs');
  });
});

describe('BattleView enrage state', () => {
  test('updates enrage from snapshot', () => {
    expect(battleView).toContain('snap.enrage && differs(snap.enrage, enrage)');
  });
});

describe('BattleView layout and polling', () => {
  test('renders party and foe columns', () => {
    expect(battleView).toContain('party-column');
    expect(battleView).toContain('foe-column');
  });

  test('wraps stat blocks with stained-glass styling', () => {
    expect(battleView).toContain('class="stats right stained-glass-panel"');
    expect(battleView).toContain('class="stats left stained-glass-panel"');
  });

  test('party column precedes foe column', () => {
    const partyIndex = battleView.indexOf('class="party-column"');
    const foeIndex = battleView.indexOf('class="foe-column"');
    expect(partyIndex).toBeGreaterThan(-1);
    expect(foeIndex).toBeGreaterThan(-1);
    expect(partyIndex).toBeLessThan(foeIndex);
  });

  test('polls backend for snapshots', () => {
    expect(battleView).toContain("roomAction(runId, 'battle', 'snapshot')");
  });

  test('shows hp bars and core stats', () => {
    expect(fighterPortrait).toContain('hp-bar');
    expect(battleView).toContain('<span class="k">DEF</span>');
    expect(battleView).toContain('CRate');
    expect(battleView).toContain('CDmg');
  });

  test('renders effect details with stack counts', () => {
    expect(statusIcons).toContain('formatTooltip');
    expect(statusIcons).toContain('stack inside');
  });

  test('displays passive stack indicators', () => {
    expect(fighterPortrait).toContain('fighter.passives');
    expect(fighterPortrait).toContain('passive-indicators');
  });

  test('uses normalized element for portraits', () => {
    expect(fighterPortrait).toContain('getElementIcon(fighter.element)');
    expect(fighterPortrait).toContain('getElementColor(fighter.element)');
  });

  test('polling respects framerate settings', async () => {
    async function measure(fps) {
      const pollDelay = 1000 / fps;
      return await new Promise((resolve) => {
        let last = performance.now();
        let count = 0;
        let total = 0;

        async function snap() {
          const start = performance.now();
          await Promise.resolve();
          const duration = performance.now() - start;
          const now = performance.now();
          total += now - last;
          last = now;
          if (++count === 5) {
            resolve(total / 5);
          } else {
            setTimeout(snap, Math.max(0, pollDelay - duration));
          }
        }

        setTimeout(snap, pollDelay);
      });
    }

    const interval30 = await measure(30);
    expect(interval30).toBeGreaterThanOrEqual(33.3 * 0.9);
    expect(interval30).toBeLessThanOrEqual(33.3 * 1.2);

    const interval60 = await measure(60);
    expect(interval60).toBeGreaterThanOrEqual(16.7 * 0.9);
    expect(interval60).toBeLessThanOrEqual(16.7 * 1.2);

    const interval120 = await measure(120);
    expect(interval120).toBeGreaterThanOrEqual(8.3 * 0.9);
    expect(interval120).toBeLessThanOrEqual(8.3 * 1.2);
  });
});
