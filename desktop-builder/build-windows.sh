#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT_DIR/desktop-dist/windows"

docker build -f desktop-builder/Dockerfile.windows -t autofighter-desktop-win "$ROOT_DIR"
docker run --rm -v "$ROOT_DIR/desktop-dist/windows:/output" autofighter-desktop-win
