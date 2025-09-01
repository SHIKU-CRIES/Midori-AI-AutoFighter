// Utilities for persisting and restoring run state.
// Stores current run id in localStorage.

const STORAGE_KEY = 'runState';

/** Load the saved run state from localStorage. */
export function loadRunState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/** Save the current run id to localStorage. */
export function saveRunState(runId) {
  if (runId) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ runId }));
  }
}

/** Remove any persisted run state. */
export function clearRunState() {
  localStorage.removeItem(STORAGE_KEY);
}
