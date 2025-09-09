import { describe, test, expect } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Guidebook wiring', () => {
  test('RunButtons has Guidebook entry', () => {
    const src = readFileSync(join(import.meta.dir, '../src/lib/components/RunButtons.svelte'), 'utf8');
    expect(src).toContain("label: 'Guidebook'");
  });

  test('Page handlers include openGuidebook', () => {
    const page = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    expect(page).toContain("openGuidebook: () => openOverlay('guidebook')");
  });

  test('OverlayHost renders Guidebook overlay', () => {
    const host = readFileSync(join(import.meta.dir, '../src/lib/components/OverlayHost.svelte'), 'utf8');
    expect(host).toContain("import Guidebook from './Guidebook.svelte'");
    expect(host).toContain("$overlayView === 'guidebook'");
  });
});

