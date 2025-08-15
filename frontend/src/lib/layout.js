export function layoutForWidth(width) {
  if (width >= 1024) return 'desktop';
  if (width >= 600) return 'tablet';
  return 'phone';
}

export function panelsForWidth(width) {
  const mode = layoutForWidth(width);
  if (mode === 'desktop') return ['menu', 'party'];
  if (mode === 'tablet') return ['menu', 'party'];
  return ['menu'];
}
