import { describe, expect, test } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';
import { FEEDBACK_URL } from '../src/lib/constants.js';

describe('Feedback button', () => {
  test('page provides a feedback link', () => {
    const page = readFileSync(join(import.meta.dir, '../src/routes/+page.svelte'), 'utf8');
    const buttons = readFileSync(join(import.meta.dir, '../src/lib/RunButtons.svelte'), 'utf8');
    expect(buttons).toContain('MessageSquare');
    expect(page).toContain('openFeedback');
    expect(page).toContain('FEEDBACK_URL');
    expect(page).toContain("window.open(FEEDBACK_URL, '_blank', 'noopener')");
    expect(FEEDBACK_URL).toBe(
      'https://github.com/Midori-AI-OSS/Midori-AI-AutoFighter/issues/new'
    );
  });
});
