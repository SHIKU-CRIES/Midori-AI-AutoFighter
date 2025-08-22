// OverlayController.js
// Central store for managing overlay view state with a simple stack.
// Components can open overlays, go back, or return home.
import { writable, get } from 'svelte/store';

export const overlayView = writable('main');
const stack = [];

export function openOverlay(view) {
  stack.push(get(overlayView));
  overlayView.set(view);
}

export function backOverlay() {
  overlayView.set(stack.pop() || 'main');
}

export function homeOverlay() {
  stack.length = 0;
  overlayView.set('main');
}
