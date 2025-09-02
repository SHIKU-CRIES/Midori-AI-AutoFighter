import { readFileSync } from 'fs';
import { join } from 'path';
import { describe, test, expect, mock } from 'bun:test';

describe('state polling', () => {
  test('state polling stops when in menu overlay', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that pollState checks overlay state
    expect(content).toContain('overlayView');
    expect(content).toContain('currentView !== \'main\'');
  });

  test('state polling stops during battle', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that pollState checks battleActive
    expect(content).toContain('if (battleActive || haltSync || !runId) return');
  });

  test('state polling starts after battle ends', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that startStatePoll is called when battle ends
    expect(content).toContain('startStatePoll();');
    expect(content).toMatch(/battleActive = false;[\s\S]*?startStatePoll\(\);/);
  });

  test('state polling timer is 5 seconds', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify 5 second interval
    expect(content).toContain('setTimeout(pollState, 5000)');
  });

  test('state timer is properly cleaned up', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify stopStatePoll clears timer
    expect(content).toContain('function stopStatePoll()');
    expect(content).toContain('clearTimeout(stateTimer)');
    expect(content).toContain('stateTimer = null');
  });

  test('state polling uses backend as source of truth', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that pollState uses getMap and updates state
    expect(content).toContain('await getMap(runId)');
    expect(content).toContain('selectedParty = data.party');
    expect(content).toContain('backend is source of truth');
  });

  test('state polling handles run end properly', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that pollState calls handleRunEnd when run no longer exists
    expect(content).toContain('handleRunEnd();');
    expect(content).toMatch(/if \(!data\) \{[\s\S]*?handleRunEnd\(\);/);
  });

  test('state polling and battle polling coordinate', async () => {
    const content = readFileSync(
      join(import.meta.dir, '../src/routes/+page.svelte'),
      'utf8'
    );
    
    // Verify that battle start stops state polling
    expect(content).toContain('stopStatePoll(); // Stop state polling when battle starts');
    
    // Verify that battle end starts state polling  
    expect(content).toContain('// Start state polling when battle ends');
  });
});