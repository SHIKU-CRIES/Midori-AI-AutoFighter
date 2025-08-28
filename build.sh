#!/bin/bash

# Build script for Midori AutoFighter
# Usage: ./build.sh [variant] [platform]
# Variants: non-llm, llm-cpu, llm-cuda, llm-amd
# Platforms: linux, windows, android (auto-detected if not specified)

set -e

VARIANT=${1:-non-llm}
PLATFORM=${2:-$(uname -s | tr '[:upper:]' '[:lower:]')}

echo "Building Midori AutoFighter - Variant: $VARIANT, Platform: $PLATFORM"

# Handle Android builds separately using Capacitor
if [ "$PLATFORM" = "android" ]; then
    echo "Building Android APK..."
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    bun install
    bun run build
    cd ..
    
    # Build mobile app
    echo "Building mobile app with Capacitor..."
    cd build/mobile
    bun install
    bun run sync
    cd android
    ./gradlew assembleDebug
    
    echo "Android build completed!"
    echo "Output: build/mobile/android/app/build/outputs/apk/debug/"
    exit 0
fi

# Desktop builds (Windows/Linux) - build backend + frontend
echo "Building desktop application..."

# Build frontend first
echo "Building frontend..."
cd frontend
bun install
bun run build
cd ..

# Build backend
echo "Setting up backend build environment..."
cd backend

# Setup environment
echo "Installing backend dependencies..."
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

# Build executable
echo "Building executable..."
DATA_ARGS="--add-data ../frontend/build"
if [ "$PLATFORM" = "windows" ]; then
    DATA_ARGS="$DATA_ARGS;frontend"
else
    DATA_ARGS="$DATA_ARGS:frontend"
fi

OUTPUT_NAME="midori-autofighter-$VARIANT-$PLATFORM"
if [ "$PLATFORM" = "windows" ]; then
    OUTPUT_NAME="$OUTPUT_NAME.exe"
fi

echo "Building: $OUTPUT_NAME"
uv run pyinstaller --onefile $DATA_ARGS --clean --name "$OUTPUT_NAME" app.py

echo "Build completed successfully!"
echo "Output: dist/$OUTPUT_NAME"
echo "Size: $(du -h dist/$OUTPUT_NAME | cut -f1)"