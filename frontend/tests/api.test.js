import { describe, expect, test, mock } from 'bun:test';
import { startRun, updateParty, fetchMap, getPlayers } from '../src/lib/api.js';

// Helper to mock fetch
function createFetch(response) {
  return mock(async () => ({ json: async () => response }));
}

describe('api calls', () => {
  test('startRun returns run data', async () => {
    global.fetch = createFetch({ run_id: '123', map: [] });
    const result = await startRun();
    expect(result).toEqual({ run_id: '123', map: [] });
  });

  test('updateParty sends party', async () => {
    global.fetch = createFetch({ status: 'ok' });
    const result = await updateParty('abc', ['sample_player']);
    expect(result).toEqual({ status: 'ok' });
  });

  test('fetchMap retrieves map', async () => {
    global.fetch = createFetch({ map: ['start'] });
    const result = await fetchMap('abc');
    expect(result).toEqual({ map: ['start'] });
  });

  test('getPlayers retrieves roster', async () => {
    global.fetch = createFetch({ players: [{ id: 'sample_player', owned: true }] });
    const result = await getPlayers();
    expect(result).toEqual({ players: [{ id: 'sample_player', owned: true }] });
  });
});
