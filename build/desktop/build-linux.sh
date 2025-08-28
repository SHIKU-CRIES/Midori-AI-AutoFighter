#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$ROOT_DIR/desktop-dist/linux"

docker build -f build/desktop/Dockerfile.linux -t autofighter-desktop-linux "$ROOT_DIR"
docker run --rm -v "$ROOT_DIR/desktop-dist/linux:/output" autofighter-desktop-linux
