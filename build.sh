#!/bin/bash

# Build script for Midori AutoFighter
# Usage: ./build.sh [variant] [platform]
# Variants: non-llm, llm-cpu, llm-cuda, llm-amd
# Platforms: linux, windows, android (auto-detected if not specified)

set -e

VARIANT=${1:-non-llm}
PLATFORM=${2:-$(uname -s | tr '[:upper:]' '[:lower:]')}

echo "Building Midori AutoFighter - Variant: $VARIANT, Platform: $PLATFORM"

# Change to legacy directory
cd "$(dirname "$0")/legacy" || exit 1

# Setup environment
echo "Setting up build environment..."
uv sync

# Install variant-specific dependencies
case "$VARIANT" in
    "llm-cpu")
        echo "Installing CPU LLM dependencies..."
        uv sync --extra llm-cpu
        ;;
    "llm-cuda")
        echo "Installing CUDA LLM dependencies..."
        uv sync --extra llm-cuda
        ;;
    "llm-amd")
        echo "Installing AMD LLM dependencies..."
        uv sync --extra llm-amd
        ;;
    "non-llm")
        echo "Using base dependencies (no LLM)..."
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: non-llm, llm-cpu, llm-cuda, llm-amd"
        exit 1
        ;;
esac

# Install PyInstaller
echo "Installing PyInstaller..."
uv add --dev pyinstaller

# Create asset directories if they don't exist
echo "Setting up asset directories..."
mkdir -p photos music

# Build executable
echo "Building executable..."
DATA_ARGS=""
if [ -d "photos" ]; then
    if [ "$PLATFORM" = "windows" ]; then
        DATA_ARGS="$DATA_ARGS --add-data photos;photos"
    else
        DATA_ARGS="$DATA_ARGS --add-data photos:photos"
    fi
fi
if [ -d "music" ]; then
    if [ "$PLATFORM" = "windows" ]; then
        DATA_ARGS="$DATA_ARGS --add-data music;music"
    else
        DATA_ARGS="$DATA_ARGS --add-data music:music"
    fi
fi

OUTPUT_NAME="midori-autofighter-$VARIANT-$PLATFORM"
if [ "$PLATFORM" = "windows" ]; then
    OUTPUT_NAME="$OUTPUT_NAME.exe"
fi

echo "Building: $OUTPUT_NAME"
uv run pyinstaller --onefile $DATA_ARGS --clean --name "$OUTPUT_NAME" main.py

echo "Build completed successfully!"
echo "Output: dist/$OUTPUT_NAME"
echo "Size: $(du -h dist/$OUTPUT_NAME | cut -f1)"