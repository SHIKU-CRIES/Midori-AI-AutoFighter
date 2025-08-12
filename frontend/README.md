# Frontend

Svelte-based GUI served with Bun on port `59001`.

## Setup

```bash
cd frontend
bun install
bun dev
```

The development server runs at `http://localhost:59001` and displays a
high-contrast icon grid powered by `lucide-svelte`. Clicking **Run** opens a
modal party picker that fetches available characters from the backend and only
shows those you own plus your avatar. After confirming the lineup the app starts
a run, saves the party, and shows the generated map as a row of buttons.

