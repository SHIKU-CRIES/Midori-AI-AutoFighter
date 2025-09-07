import { openOverlay } from './OverlayController.js';
import { httpRequest, httpGet, httpPost, httpPut, httpBlob } from './httpClient.js';

export async function getBackendFlavor() {
  try {
    const data = await httpGet('/', { cache: 'no-store' }, true); // suppress overlay for this check
    return data.flavor;
  } catch (e) {
    // Show a dedicated overlay when the backend isn't reachable/ready
    openOverlay('backend-not-ready', { message: e?.message || 'Backend unavailable' });
    throw e;
  }
}

// Health check for the backend performance endpoint
export async function getBackendHealth() {
  try {
    const networkMsStart = performance.now();
    const data = await httpRequest('/api/performance/health', {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    }, null, true); // suppress overlay for health checks
    
    const ping_ms = data?.ping_ms || (performance.now() - networkMsStart);
    const status = data?.status || (data?.health?.status) || 'ok';
    
    return { status, ping_ms };
  } catch {
    return { status: 'error', ping_ms: null };
  }
}

export async function getPlayers() {
  return httpGet('/players', { cache: 'no-store' });
}

export async function getGacha() {
  return httpGet('/gacha', { cache: 'no-store' });
}

export async function pullGacha(count = 1) {
  return httpPost('/gacha/pull', { count });
}

export async function setAutoCraft(enabled) {
  return httpPost('/gacha/auto-craft', { enabled });
}

export async function craftItems() {
  return httpPost('/gacha/craft');
}

// Player customization (pronouns, damage_type, hp, attack, defense, crit_rate, crit_damage)
export async function getPlayerConfig() {
  return httpGet('/player/editor', { cache: 'no-store' });
}

export async function savePlayerConfig(config) {
  return httpPut('/player/editor', config);
}

export async function endRun(runId) {
  return httpRequest(`/run/${runId}`, { method: 'DELETE' }, (r) => r.ok);
}

export async function endAllRuns() {
  return httpRequest('/runs', { method: 'DELETE' }, (r) => r.ok);
}

export async function wipeData() {
  return httpPost('/save/wipe');
}

export async function exportSave() {
  return httpBlob('/save/backup', { cache: 'no-store' });
}

export async function importSave(file) {
  return httpRequest('/save/restore', {
    method: 'POST',
    body: await file.arrayBuffer(),
    headers: {} // Remove default Content-Type for binary upload
  });
}

export async function getLrmConfig() {
  return httpGet('/config/lrm', { cache: 'no-store' });
}

export async function setLrmModel(model) {
  return httpPost('/config/lrm', { model });
}

export async function testLrmModel(prompt) {
  return httpPost('/config/lrm/test', { prompt });
}

// Catalog: card/relic metadata for inventory and builders
export async function getCardCatalog() {
  const data = await httpGet('/catalog/cards', { cache: 'no-store' }, true);
  return data.cards || [];
}

export async function getRelicCatalog() {
  const data = await httpGet('/catalog/relics', { cache: 'no-store' }, true);
  return data.relics || [];
}

export async function getUpgrade(id) {
  return httpGet(`/players/${id}/upgrade`, { cache: 'no-store' });
}

// New upgrade API: requires star_level (1-4) and item_count (>=1)
export async function upgradeCharacter(id, starLevel, itemCount = 1) {
  return httpPost(`/players/${id}/upgrade`, { 
    star_level: starLevel, 
    item_count: itemCount 
  });
}

// Spend upgrade points on a specific stat for the given character
export async function upgradeStat(id, points, statName = 'atk') {
  return httpPost(`/players/${id}/upgrade-stat`, { 
    points, 
    stat_name: statName 
  });
}
