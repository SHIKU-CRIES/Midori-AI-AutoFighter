import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('PullResultsOverlay component', () => {
  test('queues results and reveals sequentially', () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/lib/components/PullResultsOverlay.svelte'),
      'utf8'
    );
    expect(content).toContain('CurioChoice');
    expect(content).toContain('queue = Array.isArray(results) ? [...results] : []');
    expect(content).toContain('setTimeout(showNext');
  });
});
