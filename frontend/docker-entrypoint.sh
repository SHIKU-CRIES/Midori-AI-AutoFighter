#!/usr/bin/env bash
set -euo pipefail

cd /app

# Always ensure dependencies are installed (handles stale bind-mounted node_modules)
bun install

mkdir -p logs

exec bun run dev --host 0.0.0.0 --port 59001 2>&1 | tee -a logs/webui.log
