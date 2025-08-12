import { describe, expect, test } from 'bun:test';
import { layoutForWidth, panelsForWidth } from '../src/lib/layout.js';

describe('layoutForWidth', () => {
  test('detects desktop', () => {
    expect(layoutForWidth(1200)).toBe('desktop');
  });

  test('detects tablet', () => {
    expect(layoutForWidth(800)).toBe('tablet');
  });

  test('detects phone', () => {
    expect(layoutForWidth(400)).toBe('phone');
  });
});

describe('panelsForWidth', () => {
  test('desktop shows all panels', () => {
    expect(panelsForWidth(1200)).toEqual(['menu', 'party', 'editor', 'stats']);
  });

  test('tablet shows menu and party picker', () => {
    expect(panelsForWidth(800)).toEqual(['menu', 'party']);
  });

  test('phone shows menu only', () => {
    expect(panelsForWidth(400)).toEqual(['menu']);
  });
});
