// Global client-side error handler for SvelteKit
// Converts unhandled load/navigation errors into our error overlay.
import { openOverlay } from '$lib';

/** @type {import('@sveltejs/kit').HandleClientError} */
export function handleError({ error, event }) {
  try {
    const message = error?.message ?? String(error ?? 'Unknown error');
    const traceback = error?.stack ?? '';
    openOverlay('error', { message, traceback });
    console.error('Client error:', message, '\n', traceback, '\nAt:', event?.url?.href);
  } catch (e) {
    console.error('Failed to open error overlay', e);
  }
  return { message: error?.message ?? 'An unexpected error occurred.' };
}

// As an additional safety net, capture window-level errors
if (typeof window !== 'undefined') {
  window.addEventListener('error', (ev) => {
    const msg = ev?.error?.message || ev?.message || 'Unexpected error';
    const stack = ev?.error?.stack || '';
    openOverlay('error', { message: msg, traceback: stack });
  });
  window.addEventListener('unhandledrejection', (ev) => {
    const reason = ev?.reason;
    const msg = reason?.message || String(reason || 'Unhandled rejection');
    const stack = reason?.stack || '';
    openOverlay('error', { message: msg, traceback: stack });
  });
}

