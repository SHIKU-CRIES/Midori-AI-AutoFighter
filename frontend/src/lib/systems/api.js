import { openOverlay } from './OverlayController.js';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:59002';

async function handleFetch(url, options = {}, parser = (r) => r.json()) {
  try {
    const res = await fetch(url, options);
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
    const data = await handleFetch(`${API_BASE}/`, { cache: 'no-store', noOverlay: true });
    return data.flavor;
  } catch (e) {
    // Show a dedicated overlay when the backend isn't reachable/ready
    openOverlay('backend-not-ready', { apiBase: API_BASE, message: e?.message || 'Backend unavailable' });
    throw e;
  }
}

// Health check for the backend performance endpoint
export async function getBackendHealth() {
  const url = `${API_BASE}/api/performance/health`;
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
  return handleFetch(`${API_BASE}/players`, { cache: 'no-store' });
}

export async function getGacha() {
  return handleFetch(`${API_BASE}/gacha`, { cache: 'no-store' });
}

export async function pullGacha(count = 1) {
  return handleFetch(
    `${API_BASE}/gacha/pull`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count })
    }
  );
}

export async function setAutoCraft(enabled) {
  return handleFetch(`${API_BASE}/gacha/auto-craft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled })
  });
}

export async function craftItems() {
  return handleFetch(`${API_BASE}/gacha/craft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
}

export async function getPlayerConfig() {
  return handleFetch(`${API_BASE}/player/editor`, { cache: 'no-store' });
}

export async function savePlayerConfig(config) {
  return handleFetch(`${API_BASE}/player/editor`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
}

export async function endRun(runId) {
  return handleFetch(
    `${API_BASE}/run/${runId}`,
    { method: 'DELETE' },
    (r) => r.ok
  );
}

export async function endAllRuns() {
  return handleFetch(
    `${API_BASE}/runs`,
    { method: 'DELETE' },
    (r) => r.ok
  );
}

export async function wipeData() {
  return handleFetch(`${API_BASE}/save/wipe`, { method: 'POST' });
}

export async function exportSave() {
  return handleFetch(
    `${API_BASE}/save/backup`,
    { cache: 'no-store' },
    (r) => r.blob()
  );
}

export async function importSave(file) {
  return handleFetch(`${API_BASE}/save/restore`, {
    method: 'POST',
    body: await file.arrayBuffer()
  });
}

export async function getLrmConfig() {
  return handleFetch(`${API_BASE}/config/lrm`, { cache: 'no-store' });
}

export async function setLrmModel(model) {
  return handleFetch(`${API_BASE}/config/lrm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model })
  });
}

export async function testLrmModel(prompt) {
  return handleFetch(`${API_BASE}/config/lrm/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
}

// Catalog: card/relic metadata for inventory and builders
export async function getCardCatalog() {
  const data = await handleFetch(`${API_BASE}/catalog/cards`, { cache: 'no-store', noOverlay: true });
  return data.cards || [];
}

export async function getRelicCatalog() {
  const data = await handleFetch(`${API_BASE}/catalog/relics`, { cache: 'no-store', noOverlay: true });
  return data.relics || [];
}

export async function getUpgrade(id) {
  return handleFetch(`${API_BASE}/players/${id}/upgrade`, { cache: 'no-store' });
}

// New upgrade API: requires star_level (1-4) and item_count (>=1)
export async function upgradeCharacter(id, starLevel, itemCount = 1) {
  return handleFetch(`${API_BASE}/players/${id}/upgrade`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ star_level: starLevel, item_count: itemCount })
  });
}

// Spend player upgrade points on a specific stat (player only)
export async function upgradePlayerStat(points, statName = 'atk') {
  return handleFetch(`${API_BASE}/players/player/upgrade-stat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ points, stat_name: statName })
  });
}
