import { describe, expect, test, mock } from 'bun:test';
import { getPlayers } from '../src/lib/api.js';
import { overlayView, overlayData, homeOverlay } from '../src/lib/OverlayController.js';
import { get } from 'svelte/store';
import { readFileSync } from 'fs';
import { join } from 'path';
import { FEEDBACK_URL } from '../src/lib/constants.js';

describe('Error overlay', () => {
  test('opens when fetch fails', async () => {
    homeOverlay();
    const payload = { message: 'Boom', traceback: 'stack trace' };
    global.fetch = mock(async () => ({ ok: false, status: 500, json: async () => payload }));
    await expect(getPlayers()).rejects.toThrow('Boom');
    expect(get(overlayView)).toBe('error');
    expect(get(overlayData)).toEqual(payload);
  });

  test('report button uses feedback url', () => {
    const content = readFileSync(join(import.meta.dir, '../src/lib/ErrorOverlay.svelte'), 'utf8');
    expect(content).toContain('Report Issue');
    expect(content).toContain('FEEDBACK_URL');
    expect(FEEDBACK_URL).toBe('https://github.com/Midori-AI-OSS/Midori-AI-AutoFighter/issues/new');
  });
});
