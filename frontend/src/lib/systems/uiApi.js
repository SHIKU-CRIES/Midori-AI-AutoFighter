// UI-centric API for communicating with backend
// Replaces the run-specific API with a simpler state-based approach

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
        message = data.message || data.error || '';
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
      err.overlayShown = res.status !== 404;
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
      try { console.error('API failure:', { url: fullUrl, message: msg }); } catch {}
    }
    throw e;
  }
}

/**
 * Get the complete UI state from the backend.
 * Returns the current UI mode, game state, and available actions.
 */
export async function getUIState() {
  try {
    return await handleFetch('/ui');
  } catch (e) {
    if (!e.overlayShown) {
      let msg = (typeof e?.message === 'string' && e.message) || String(e ?? 'Unknown error');
      msg = String(msg || '').trim();
      if (/^\d+$/.test(msg)) {
        msg = `Unexpected error (code ${msg}) during getUIState`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('getUIState failure:', { message: msg }); } catch {}
    }
    throw e;
  }
}

/**
 * Send an action to the backend.
 * @param {string} action - The action to perform
 * @param {object} params - Action-specific parameters
 */
export async function sendAction(action, params = {}) {
  try {
    return await handleFetch('/ui/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, params })
    });
  } catch (e) {
    if (!e.overlayShown) {
      let msg = (typeof e?.message === 'string' && e.message) || String(e ?? 'Unknown error');
      msg = String(msg || '').trim();
      if (/^\d+$/.test(msg)) {
        msg = `Unexpected error (code ${msg}) during sendAction ${action}`;
      }
      openOverlay('error', { message: msg, traceback: e?.stack || '' });
      try { console.error('sendAction failure:', { action, params, message: msg }); } catch {}
    }
    throw e;
  }
}

/**
 * Start a new run with the specified party.
 * @param {Array} party - List of party member IDs
 * @param {string} damageType - Damage type for the player
 * @param {number} pressure - Pressure setting
 */
export async function startRun(party, damageType = '', pressure = 0) {
  return await sendAction('start_run', { 
    party: party || ['player'], 
    damage_type: damageType, 
    pressure 
  });
}

/**
 * Perform a room action.
 * @param {string} roomId - The room ID (typically "0" for current room)
 * @param {object|string} actionData - Action-specific data
 */
export async function roomAction(roomId = '0', actionData = {}) {
  const params = { room_id: roomId };
  if (actionData && typeof actionData === 'object') {
    Object.assign(params, actionData);
  } else if (actionData) {
    params.action = actionData;
  }
  return await sendAction('room_action', params);
}

/**
 * Advance to the next room.
 */
export async function advanceRoom() {
  const state = await getUIState();
  const gs = state?.game_state || {};
  const cs = gs?.current_state || {};
  if (cs.awaiting_card || cs.awaiting_relic || cs.awaiting_loot) {
    const message = 'Cannot advance room until all rewards are collected.';
    openOverlay('error', { message, traceback: '' });
    const err = new Error(message);
    err.status = 400;
    err.overlayShown = true;
    throw err;
  }
  return await sendAction('advance_room');
}

/**
 * Choose a card reward.
 * @param {string} cardId - The card ID to choose
 */
export async function chooseCard(cardId) {
  return await sendAction('choose_card', { card_id: cardId });
}

/**
 * Choose a relic reward.
 * @param {string} relicId - The relic ID to choose
 */
export async function chooseRelic(relicId) {
  return await sendAction('choose_relic', { relic_id: relicId });
}

/**
 * Acknowledge and collect room loot.
 * @param {string} runId - The current run identifier
 */
export async function acknowledgeLoot(runId) {
  return await handleFetch(`/rewards/loot/${runId}`, {
    method: 'POST'
  });
}

// For backward compatibility with existing code, we can provide fallback functions
// that use the old API format but internally use the new UI API

/**
 * @deprecated Use getUIState() instead
 */
export async function getMap(_runId) {
  const uiState = await getUIState();
  if (uiState.mode === 'menu') {
    return null; // Simulate run not found
  }
  return uiState.game_state;
}

/**
 * @deprecated Use getUIState() instead  
 */
export async function getActiveRuns() {
  const uiState = await getUIState();
  if (uiState.active_run) {
    return {
      runs: [{
        run_id: uiState.active_run,
        party: uiState.game_state?.party || [],
        map: uiState.game_state?.map || {}
      }]
    };
  }
  return { runs: [] };
}

/**
 * Update the current party selection on the backend.
 * @param {Array} party - List of party member IDs
 */
export async function updateParty(party) {
  return await sendAction('update_party', { party });
}

/**
 * Retrieve a battle summary for the current run.
 * @param {number} battleIndex - Index of the battle to fetch
 */
export async function getBattleSummary(battleIndex) {
  return handleFetch(`/battles/${battleIndex}/summary`, { cache: 'no-store' });
}

/**
 * Retrieve detailed battle events for the current run.
 * @param {number} battleIndex - Index of the battle to fetch
 */
export async function getBattleEvents(battleIndex) {
  return handleFetch(`/battles/${battleIndex}/events`, { cache: 'no-store' });
}

/**
 * Fetch catalog data for relics, cards, DoTs, and HoTs.
 */
export async function getCatalogData() {
  const [relics, cards, dots, hots] = await Promise.all([
    handleFetch(`/catalog/relics`),
    handleFetch(`/catalog/cards`),
    handleFetch(`/catalog/dots`),
    handleFetch(`/catalog/hots`),
  ]);

  return {
    relics: relics.relics || [],
    cards: cards.cards || [],
    dots: dots.dots || [],
    hots: hots.hots || [],
  };
}
