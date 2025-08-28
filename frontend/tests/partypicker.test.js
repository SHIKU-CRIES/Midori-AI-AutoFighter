import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('PartyPicker component', () => {
  test('contains party picker markup', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/PartyPicker.svelte'), 'utf8');
    expect(content).toContain('data-testid="party-picker"');
  });

  test('includes add/remove control', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/StatTabs.svelte'), 'utf8');
    expect(content).toContain('Add to party');
  });

  test('references updated stat keys', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/StatTabs.svelte'), 'utf8');
    expect(content).toContain('crit_damage');
    expect(content).toContain('effect_hit_rate');
    expect(content).toContain('dodge_odds');
    expect(content).toContain('effect_resistance');
  });

  test('filters unowned characters and normalizes element names', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/PartyPicker.svelte'), 'utf8');
    expect(content).toContain('filter((p) => p.owned || p.is_player)');
    expect(content).toContain('selected = selected.filter((id) => roster.some((c) => c.id === id))');
    expect(content).toContain('element: resolveElement(p)');
  });

  test('orders stats correctly', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/StatTabs.svelte'), 'utf8');
    const coreStart = content.indexOf("{#if activeTab === 'Core'}");
    const coreEnd = content.indexOf("{:else if activeTab === 'Offense'}");
    const coreSection = content.slice(coreStart, coreEnd);
    expect(coreSection).toMatch(/HP[\s\S]*EXP[\s\S]*Vitality[\s\S]*Regain/);
    expect(coreSection).not.toMatch(/DEF/);
    const defStart = content.indexOf("{:else if activeTab === 'Defense'}");
    const defEnd = content.indexOf('{/if}', defStart);
    const defSection = content.slice(defStart, defEnd);
    expect(defSection).toMatch(/<div><span>DEF<\/span><span>{sel.stats.defense/);
  });

  test('uses element colors for icon and outline', () => {
    const rosterContent = readFileSync(join(import.meta.dir, '../src/lib/PartyRoster.svelte'), 'utf8');
    expect(rosterContent).toContain('style={`border-color: ${getElementColor(char.element)}`}');
    expect(rosterContent).toContain('style={`color: ${getElementColor(char.element)}`}');
  });

  test('roster layout snapshot', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/PartyRoster.svelte'), 'utf8');
    expect(content).toMatchSnapshot();
  });
});

