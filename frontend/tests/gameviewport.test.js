import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Viewport modularization', () => {
  test('sidebar disables items during battle', () => {
    const menu = readFileSync(join(import.meta.dir, '../src/lib/MainMenu.svelte'), 'utf8');
    const viewport = readFileSync(join(import.meta.dir, '../src/lib/GameViewport.svelte'), 'utf8');
    expect(viewport).toContain('battleActive');
    expect(menu).toContain('disabled={item.disabled}');
  });

  test('NavBar switches icon during combat', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/NavBar.svelte'), 'utf8');
    expect(content).toContain('{#if battleActive}');
    expect(content).toContain('<Swords');
  });

  test('sidebar hidden when battle active', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/GameViewport.svelte'), 'utf8');
    expect(content).toContain("$overlayView === 'main' && !battleActive");
  });

  test('start run overlay uses stained glass buttons', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/OverlayHost.svelte'), 'utf8');
    expect(content).toContain('stained-glass-row');
    expect(content).toContain('Start Run');
    expect(content).toContain('Cancel');
  });

  test('party save dispatch exists', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/OverlayHost.svelte'), 'utf8');
    expect(content).toContain("dispatch('saveParty')");
  });

  test('NavBar emits navigation events', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/NavBar.svelte'), 'utf8');
    expect(content).toContain("dispatch('home')");
    expect(content).toContain("dispatch('openEditor')");
    expect(content).toContain("dispatch('back')");
  });

  test('Review overlay referenced', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/OverlayHost.svelte'), 'utf8');
    expect(content).toContain('BattleReview');
    expect(content).toContain('relic_choices');
    expect(content).toContain('card_choices');
  });
});
