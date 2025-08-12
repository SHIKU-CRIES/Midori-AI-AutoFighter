#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the mounted app directory
cd /app

# Optional extras via UV_EXTRA
if [[ -n "${UV_EXTRA:-}" ]]; then
  uv sync --extra "$UV_EXTRA"
else
  uv sync
fi

# Default DB lives under /app/save.db; override via AF_DB_PATH if needed
export PYTHONPATH="/app:${PYTHONPATH:-}"

exec uv run app.py

