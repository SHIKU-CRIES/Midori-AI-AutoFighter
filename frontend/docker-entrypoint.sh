#!/usr/bin/env bash
set -euo pipefail

cd /app

# Always ensure dependencies are installed (handles stale bind-mounted node_modules)
bun install

# Build the Svelte app before first load (one-time unless build/ is cleared)
if [[ ! -f "build/index.html" ]]; then
  echo "[frontend] First run detected: building static assets..."
  bun run build
  echo "[frontend] Build complete."
fi

# Give the backend time to boot before starting the dev server
echo "[frontend] Waiting 25s for backend to start..."
sleep 25

mkdir -p logs

exec bun run dev --host 0.0.0.0 --port 59001 2>&1 | tee -a logs/webui.log
