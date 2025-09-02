// Lightweight wrappers for run-related API calls.
// Each helper talks to the backend and returns JSON payloads.

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

async function handleFetch(url, options = {}) {
  // Ensure we have the API base before making the request
  const apiBase = await ensureApiBase();
  
  // If url is relative, prepend the API base
  const fullUrl = url.startsWith('http') ? url : `${apiBase}${url.startsWith('/') ? '' : '/'}${url}`;
  
  try {
    const res = await fetch(fullUrl, options);
    if (!res.ok) {
      let data; let message = ''; let traceback = '';
      try { data = await res.json(); } catch {}
      if (data && typeof data === 'object') {
        message = data.message || '';
        traceback = data.traceback || '';
      }
      if (!message) {
        try {
          const text = await res.text();
          message = (text && text.trim()) || '';
        } catch {}
      }
      if (!message) message = `HTTP error ${res.status}`;
      // Normalize bare numeric bodies to a descriptive error
      const trimmed = String(message || '').trim();
      if (/^\d+$/.test(trimmed)) {
        message = `Unexpected backend error (code ${trimmed}) during ${options?.method || 'GET'} ${fullUrl}`;
      }
      // Suppress global error overlays for 404s; callers may treat them as transient
      if (res.status !== 404) {
        openOverlay('error', { message, traceback });
        try { console.error('API error:', { url: fullUrl, status: res.status, message, traceback }); } catch {}
      }
      const err = new Error(message);
      err.status = res.status;
      // Mark as handled for both 404s (transient) and explicit overlay cases
      err.overlayShown = true;
      throw err;
    }
    return res.json();
  } catch (e) {
    if (!e.overlayShown) {
      let msg = (typeof e?.message === 'string' && e.message) || String(e ?? 'Unknown error');
      msg = String(msg || '').trim();
      if (/^\d+$/.test(msg)) {
        msg = `Unexpected error (code ${msg}) during ${options?.method || 'GET'} ${fullUrl}`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('Fetch failure:', { url: fullUrl, message: msg }); } catch {}
    }
    throw e;
  }
}

export async function getActiveRuns() {
  return handleFetch(`/runs`);
}

export async function startRun(party, damageType = '', pressure = 0) {
  return handleFetch(`/run/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ party, damage_type: damageType, pressure })
  });
}

export async function getMap(runId) {
  try {
    const apiBase = await ensureApiBase();
    const res = await fetch(`${apiBase}/map/${runId}`, { cache: 'no-store' });
    if (res.status === 404) return null;
    if (!res.ok) {
      let data; let message = ''; let traceback = '';
      try { data = await res.json(); } catch {}
      if (data && typeof data === 'object') {
        message = data.message || '';
        traceback = data.traceback || '';
      }
      if (!message) {
        try {
          const text = await res.text();
          message = (text && text.trim()) || '';
        } catch {}
      }
      if (!message) message = `HTTP error ${res.status}`;
      const trimmed = String(message || '').trim();
      if (/^\d+$/.test(trimmed)) {
        message = `Unexpected backend error (code ${trimmed}) during GET ${apiBase}/map/${runId}`;
      }
      openOverlay('error', { message, traceback });
      try { console.error('API error:', { endpoint: 'getMap', runId, status: res.status, message }); } catch {}
      const err = new Error(message);
      err.overlayShown = true;
      throw err;
    }
    return res.json();
  } catch (e) {
    if (!e.overlayShown) {
      const apiBase = await ensureApiBase();
      let msg = (typeof e?.message === 'string' && e.message) || String(e ?? 'Unknown error');
      msg = String(msg || '').trim();
      if (/^\d+$/.test(msg)) {
        msg = `Unexpected error (code ${msg}) during GET ${apiBase}/map/${runId}`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('getMap failure:', { runId, message: msg }); } catch {}
    }
    throw e;
  }
}

export async function updateParty(runId, party) {
  return handleFetch(`/party/${runId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ party })
  });
}

export async function roomAction(runId, type, action = '') {
  const payload = (action && typeof action === 'object') ? action : { action };
  // Short-circuit snapshot polling when global sync is halted (e.g., defeat popup)
  try {
    const halted = typeof window !== 'undefined' && window.afHaltSync === true;
    const rewardPause = typeof window !== 'undefined' && window.afRewardOpen === true;
    if ((halted || rewardPause) && type === 'battle' && String(payload?.action || '') === 'snapshot') {
      return {};
    }
  } catch {}
  return handleFetch(`/rooms/${runId}/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function advanceRoom(runId) {
  return handleFetch(`/run/${runId}/next`, { method: 'POST' });
}

export async function pauseCombat(runId) {
  return roomAction(runId, 'battle', 'pause');
}

export async function resumeCombat(runId) {
  return roomAction(runId, 'battle', 'resume');
}

export async function chooseCard(runId, cardId) {
  return handleFetch(`/cards/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card: cardId })
  });
}

export async function chooseRelic(runId, relicId) {
  return handleFetch(`/relics/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ relic: relicId })
  });
}

export async function acknowledgeLoot(runId) {
  return handleFetch(`/loot/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
}

export async function getBattleSummary(runId, index) {
  // Use the backend API base; 404 is expected if summary not yet written
  const apiBase = await ensureApiBase();
  const url = `${apiBase}/run/${runId}/battles/${index}/summary`;
  const res = await fetch(url, { cache: 'no-store' });
  if (res.status === 404) {
    const err = new Error('summary not found');
    err.status = 404;
    err.overlayShown = true; // prevent global error overlay
    throw err;
  }
  if (!res.ok) {
    let data; let message = '';
    try { data = await res.json(); } catch {}
    if (data && typeof data === 'object') message = data.message || '';
    if (!message) {
      try { const text = await res.text(); message = (text && text.trim()) || ''; } catch {}
    }
    if (!message) message = `HTTP error ${res.status}`;
    const trimmed = String(message || '').trim();
    if (/^\d+$/.test(trimmed)) {
      message = `Unexpected backend error (code ${trimmed}) during GET ${url}`;
    }
    const err = new Error(message);
    err.status = res.status;
    err.overlayShown = true;
    throw err;
  }
  return res.json();
}

export async function getBattleEvents(runId, index) {
  const apiBase = await ensureApiBase();
  const url = `${apiBase}/run/${runId}/battles/${index}/events`;
  const res = await fetch(url, { cache: 'no-store' });
  if (res.status === 404) {
    const err = new Error('events not found');
    err.status = 404;
    err.overlayShown = true;
    throw err;
  }
  if (!res.ok) {
    let data; let message = '';
    try { data = await res.json(); } catch {}
    if (data && typeof data === 'object') message = data.message || '';
    if (!message) {
      try { const text = await res.text(); message = (text && text.trim()) || ''; } catch {}
    }
    if (!message) message = `HTTP error ${res.status}`;
    const trimmed = String(message || '').trim();
    if (/^\d+$/.test(trimmed)) {
      message = `Unexpected backend error (code ${trimmed}) during GET ${url}`;
    }
    const err = new Error(message);
    err.status = res.status;
    err.overlayShown = true;
    throw err;
  }
  return res.json();
}

export async function getCatalogData() {
  // Fetch all catalog data in parallel
  const [relics, cards, dots, hots] = await Promise.all([
    handleFetch(`/catalog/relics`),
    handleFetch(`/catalog/cards`),
    handleFetch(`/catalog/dots`),
    handleFetch(`/catalog/hots`)
  ]);
  
  return {
    relics: relics.relics || [],
    cards: cards.cards || [],
    dots: dots.dots || [],
    hots: hots.hots || []
  };
}
