import { describe, test, expect } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';
import { compile } from 'svelte/compiler';

describe('StarStorm component', () => {
  test('compiles to DOM', () => {
    const source = readFileSync(join(import.meta.dir, '../src/lib/components/StarStorm.svelte'), 'utf8');
    const { js } = compile(source, { generate: 'dom' });
    expect(js.code.length).toBeGreaterThan(0);
  });
});
