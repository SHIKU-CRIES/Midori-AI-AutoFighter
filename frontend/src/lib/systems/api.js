import { openOverlay } from './OverlayController.js';
import { getApiBase } from './backendDiscovery.js';

// Dynamic API base - will be resolved via backend discovery
let API_BASE = null;

async function ensureApiBase() {
  if (!API_BASE) {
    API_BASE = await getApiBase();
  }
  return API_BASE;
}

async function handleFetch(url, options = {}, parser = (r) => r.json()) {
  // Ensure we have the API base before making the request
  const apiBase = await ensureApiBase();
  
  // If url is relative, prepend the API base
  const fullUrl = url.startsWith('http') ? url : `${apiBase}${url.startsWith('/') ? '' : '/'}${url}`;
  
  try {
    const res = await fetch(fullUrl, options);
    if (!res.ok) {
      let data;
      try { data = await res.json(); } catch {}
      const message = data?.message || `HTTP error ${res.status}`;
      const traceback = data?.traceback || '';
      if (!options?.noOverlay) {
        openOverlay('error', { message, traceback });
      }
      const err = new Error(message);
      err.overlayShown = true;
      throw err;
    }
    return await parser(res);
  } catch (e) {
    if (!e.overlayShown && !options?.noOverlay) {
      openOverlay('error', { message: e.message, traceback: e.stack || '' });
    }
    throw e;
  }
}

export async function getBackendFlavor() {
  try {
    const data = await handleFetch(`/`, { cache: 'no-store', noOverlay: true });
    return data.flavor;
  } catch (e) {
    // Show a dedicated overlay when the backend isn't reachable/ready
    const apiBase = await ensureApiBase();
    openOverlay('backend-not-ready', { apiBase, message: e?.message || 'Backend unavailable' });
    throw e;
  }
}

// Health check for the backend performance endpoint
export async function getBackendHealth() {
  const apiBase = await ensureApiBase();
  const url = `${apiBase}/api/performance/health`;
  try {
    const networkMsStart = performance.now();
    const res = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
    let data = null;
    let status = 'ok';
    let ping_ms = null;
    if (res.ok) {
      try { data = await res.json(); } catch { data = null; }
      status = (data && (data.status || (data.health && data.health.status))) || 'ok';
      ping_ms = (data && data.ping_ms) || (performance.now() - networkMsStart);
    } else {
      status = 'error';
    }
    return { status, ping_ms };
  } catch {
    return { status: 'error', ping_ms: null };
  }
}

export async function getPlayers() {
  return handleFetch(`/players`, { cache: 'no-store' });
}

export async function getGacha() {
  return handleFetch(`/gacha`, { cache: 'no-store' });
}

export async function pullGacha(count = 1) {
  return handleFetch(
    `/gacha/pull`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count })
    }
  );
}

export async function setAutoCraft(enabled) {
  return handleFetch(`/gacha/auto-craft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled })
  });
}

export async function craftItems() {
  return handleFetch(`/gacha/craft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
}

// Player customization (pronouns, damage_type, hp, attack, defense, crit_rate, crit_damage)
export async function getPlayerConfig() {
  return handleFetch(`/player/editor`, { cache: 'no-store' });
}

export async function savePlayerConfig(config) {
  return handleFetch(`/player/editor`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
}

export async function endRun(runId) {
  return handleFetch(
    `/run/${runId}`,
    { method: 'DELETE' },
    (r) => r.ok
  );
}

export async function endAllRuns() {
  return handleFetch(
    `/runs`,
    { method: 'DELETE' },
    (r) => r.ok
  );
}

export async function wipeData() {
  return handleFetch(`/save/wipe`, { method: 'POST' });
}

export async function exportSave() {
  return handleFetch(
    `/save/backup`,
    { cache: 'no-store' },
    (r) => r.blob()
  );
}

export async function importSave(file) {
  return handleFetch(`/save/restore`, {
    method: 'POST',
    body: await file.arrayBuffer()
  });
}

export async function getLrmConfig() {
  return handleFetch(`/config/lrm`, { cache: 'no-store' });
}

export async function setLrmModel(model) {
  return handleFetch(`/config/lrm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model })
  });
}

export async function testLrmModel(prompt) {
  return handleFetch(`/config/lrm/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
}

// Catalog: card/relic metadata for inventory and builders
export async function getCardCatalog() {
  const data = await handleFetch(`/catalog/cards`, { cache: 'no-store', noOverlay: true });
  return data.cards || [];
}

export async function getRelicCatalog() {
  const data = await handleFetch(`/catalog/relics`, { cache: 'no-store', noOverlay: true });
  return data.relics || [];
}

export async function getUpgrade(id) {
  return handleFetch(`/players/${id}/upgrade`, { cache: 'no-store' });
}

// New upgrade API: requires star_level (1-4) and item_count (>=1)
export async function upgradeCharacter(id, starLevel, itemCount = 1) {
  return handleFetch(`/players/${id}/upgrade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ star_level: starLevel, item_count: itemCount })
  });
}

// Spend upgrade points on a specific stat for the given character
export async function upgradeStat(id, points, statName = 'atk') {
  return handleFetch(`/players/${id}/upgrade-stat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ points, stat_name: statName })
  });
}
