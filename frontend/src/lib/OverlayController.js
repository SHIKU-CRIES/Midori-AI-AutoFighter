// OverlayController.js
// Central store for managing overlay view state with a simple stack.
// Components can open overlays, go back, or return home.
import { writable, get } from 'svelte/store';

export const overlayView = writable('main');
export const overlayData = writable({});
const stack = [];

export function openOverlay(view, data = {}) {
  stack.push({ view: get(overlayView), data: get(overlayData) });
  overlayView.set(view);
  overlayData.set(data);
}

export function backOverlay() {
  const prev = stack.pop() || { view: 'main', data: {} };
  overlayView.set(prev.view);
  overlayData.set(prev.data);
}

export function homeOverlay() {
  stack.length = 0;
  overlayView.set('main');
  overlayData.set({});
}
