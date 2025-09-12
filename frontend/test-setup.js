// Test setup for bun test
// Mock SvelteKit modules that aren't available in test environment

import { beforeAll } from 'bun:test';

beforeAll(() => {
  // Mock $app/environment
  global.$app = {
    environment: {
      browser: false,
      dev: false,
      building: false,
      version: {}
    }
  };

  // Mock $app/stores  
  global.$stores = {
    page: {
      subscribe: () => () => {}
    },
    navigating: {
      subscribe: () => () => {}
    },
    updated: {
      subscribe: () => () => {}
    }
  };

  // Mock $lib modules that might be problematic
  global.fetch = global.fetch || (() => Promise.resolve({ ok: true, json: () => Promise.resolve({}) }));
});