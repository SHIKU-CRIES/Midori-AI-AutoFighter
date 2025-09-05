import { browser } from '$app/environment';

let cached = null;

export async function getApiBase() {
  if (cached) {
    return cached;
  }

  const envBase = import.meta.env && import.meta.env.VITE_API_BASE;
  if (envBase) {
    cached = envBase;
    return cached;
  }

  if (browser) {
    try {
      const res = await fetch('/api-base', { cache: 'no-store' });
      cached = await res.text();
      return cached;
    } catch {
      // fall through to default
    }
  }

  cached = 'http://localhost:59002';
  return cached;
}

export function resetDiscovery() {
  cached = null;
}

export function getCachedApiBase() {
  return cached;
}
