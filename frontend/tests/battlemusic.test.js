import { describe, expect, test } from 'bun:test';
import {
  characterLibrary,
  fallbackLibrary,
} from '../src/lib/systems/music.js';
import { selectBattleMusic } from '../src/lib/systems/viewportState.js';

characterLibrary.luna = { normal: ['/luna/theme.mp3'] };
fallbackLibrary.normal = ['/fallback/track.mp3'];

describe('battle music selection', () => {
  test("Luna's theme plays once combatants are known", () => {
    const roomType = 'battle-normal';
    const early = selectBattleMusic({ roomType, party: [], foes: [] });
    expect(early.some((t) => t.includes('/luna/'))).toBe(false);

    const playlist = selectBattleMusic({
      roomType,
      party: [{ id: 'luna' }],
      foes: [{ id: 'slime' }]
    });
    expect(playlist.some((t) => t.includes('/luna/'))).toBe(true);
  });
});
