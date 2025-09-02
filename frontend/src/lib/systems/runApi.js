// Lightweight wrappers for run-related API calls.
// Each helper talks to the backend and returns JSON payloads.

import { openOverlay } from './OverlayController.js';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:59002';

async function handleFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
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
        message = `Unexpected backend error (code ${trimmed}) during ${options?.method || 'GET'} ${url}`;
      }
      // Suppress global error overlays for 404s; callers may treat them as transient
      if (res.status !== 404) {
        openOverlay('error', { message, traceback });
        try { console.error('API error:', { url, status: res.status, message, traceback }); } catch {}
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
        msg = `Unexpected error (code ${msg}) during ${options?.method || 'GET'} ${url}`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('Fetch failure:', { url, message: msg }); } catch {}
    }
    throw e;
  }
}

export async function getActiveRuns() {
  return handleFetch(`${API_BASE}/runs`);
}

export async function startRun(party, damageType = '', pressure = 0) {
  return handleFetch(`${API_BASE}/run/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ party, damage_type: damageType, pressure })
  });
}

export async function getMap(runId) {
  try {
    const res = await fetch(`${API_BASE}/map/${runId}`, { cache: 'no-store' });
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
        message = `Unexpected backend error (code ${trimmed}) during GET ${API_BASE}/map/${runId}`;
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
      let msg = (typeof e?.message === 'string' && e.message) || String(e ?? 'Unknown error');
      msg = String(msg || '').trim();
      if (/^\d+$/.test(msg)) {
        msg = `Unexpected error (code ${msg}) during GET ${API_BASE}/map/${runId}`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('getMap failure:', { runId, message: msg }); } catch {}
    }
    throw e;
  }
}

export async function updateParty(runId, party) {
  return handleFetch(`${API_BASE}/party/${runId}`, {
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
  return handleFetch(`${API_BASE}/rooms/${runId}/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
}

export async function advanceRoom(runId) {
  return handleFetch(`${API_BASE}/run/${runId}/next`, { method: 'POST' });
}

export async function pauseCombat(runId) {
  return roomAction(runId, 'battle', 'pause');
}

export async function resumeCombat(runId) {
  return roomAction(runId, 'battle', 'resume');
}

export async function chooseCard(runId, cardId) {
  return handleFetch(`${API_BASE}/cards/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card: cardId })
  });
}

export async function chooseRelic(runId, relicId) {
  return handleFetch(`${API_BASE}/relics/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ relic: relicId })
  });
}

export async function acknowledgeLoot(runId) {
  return handleFetch(`${API_BASE}/loot/${runId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
}

export async function getBattleSummary(runId, index) {
  // Use the backend API base; 404 is expected if summary not yet written
  const url = `${API_BASE}/run/${runId}/battles/${index}/summary`;
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
  const url = `${API_BASE}/run/${runId}/battles/${index}/events`;
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
    handleFetch(`${API_BASE}/catalog/relics`),
    handleFetch(`${API_BASE}/catalog/cards`),
    handleFetch(`${API_BASE}/catalog/dots`),
    handleFetch(`${API_BASE}/catalog/hots`)
  ]);
  
  return {
    relics: relics.relics || [],
    cards: cards.cards || [],
    dots: dots.dots || [],
    hots: hots.hots || []
  };
}
