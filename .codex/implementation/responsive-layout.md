# Responsive Layout

The Svelte frontend adapts the interface to three viewport ranges:

- **Desktop (≥1024px)** – renders the party picker, player editor, and stats panel alongside the main menu so most information stays visible.
- **Tablet (600–1023px)** – shows the main menu beside the party picker for a two-panel view.
- **Phone (<600px)** – focuses on a single menu at a time for clarity on small screens.

## Testing
- `cd frontend && bun test`
