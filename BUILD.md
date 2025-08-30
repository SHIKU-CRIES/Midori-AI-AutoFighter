# Midori AutoFighter Build System

This repository contains GitHub Actions workflows to automatically build the Midori AutoFighter game for multiple platforms and configurations.

## Build Variants

### Platforms
- **Windows** (x64)
- **Linux** (x64)
- **Android** (ARM64/x64)

### Configurations
- **non-llm**: Base game without LLM support
- **llm-cpu**: Game with CPU-based LLM support
- **llm-cuda**: Game with NVIDIA GPU LLM support (CUDA)
- **llm-amd**: Game with AMD GPU LLM support (ROCm)

*Note: Android builds currently only support the non-llm variant due to size and compatibility constraints.*

## Automated Builds

### GitHub Actions Workflows

#### Individual Platform Workflows
- `.github/workflows/build-windows.yml` - Builds all 4 Windows variants
- `.github/workflows/build-linux.yml` - Builds all 4 Linux variants
- `.github/workflows/build-android.yml` - Builds Android non-llm variant

#### Comprehensive Build Workflow
- `.github/workflows/build-all-platforms.yml` - Builds all variants for all platforms

### Trigger Conditions
- **Manual dispatch** (workflow_dispatch) - All workflows require manual triggering via GitHub Actions UI
- **Git tags** starting with `v` - Only the build-all-platforms workflow auto-runs for release creation

**Note**: Automatic triggering on push and pull requests has been disabled. Build workflows must be manually initiated by clicking "Run workflow" in the GitHub Actions tab, except for the release process which still triggers automatically on version tags.

### Build Artifacts
All builds are automatically uploaded as GitHub Actions artifacts with 30-day retention:
- `midori-autofighter-{variant}-{platform}.exe` (Windows)
- `midori-autofighter-{variant}-{platform}` (Linux)
- `midori-autofighter-non-llm-android.apk` (Android)

### Releases
When you push a git tag starting with `v` (e.g., `v1.0.0`), the build-all-platforms workflow will automatically:
1. Build all variants for all platforms
2. Create a GitHub release
3. Upload all build artifacts to the release

**Note**: This is the only remaining automatic trigger - releases still work automatically when you push version tags.

## Local Development

### Prerequisites
- [uv](https://github.com/astral-sh/uv) for Python dependency management
- Python 3.12+

### Quick Build
Use the provided build script:

```bash
# Build non-llm variant for current platform
./build.sh

# Build specific variant
./build.sh llm-cpu

# Build for specific platform
./build.sh non-llm linux
./build.sh llm-cuda windows
```

### Manual Build Process

1. **Setup environment:**
   ```bash
   cd legacy
   uv sync
   ```

2. **Install variant dependencies (if needed):**
   ```bash
   # For LLM variants:
   uv sync --extra llm-cpu     # CPU LLM support
   uv sync --extra llm-cuda    # NVIDIA GPU LLM support
   uv sync --extra llm-amd     # AMD GPU LLM support
   ```

3. **Install PyInstaller:**
   ```bash
   uv add --dev pyinstaller
   ```

4. **Create asset directories:**
   ```bash
   mkdir -p photos music
   ```

5. **Build executable:**
   ```bash
   # Linux/macOS
   uv run pyinstaller --onefile --add-data photos:photos --add-data music:music --clean --name midori-autofighter main.py
   
   # Windows (if using cross-platform)
   uv run pyinstaller --onefile --add-data photos;photos --add-data music;music --clean --name midori-autofighter main.py
   ```

### Dependencies by Variant

#### Base Dependencies (all variants)
- colorama >= 0.4.6
- halo >= 0.0.31
- pygame >= 2.6.1
- snakeviz >= 2.2.2

#### LLM Dependencies
- **llm-cpu**: torch, transformers, accelerate
- **llm-cuda**: torch, transformers, accelerate, nvidia-ml-py
- **llm-amd**: torch, transformers, accelerate (with ROCm support)

## Android Build Notes

Android builds use a different approach:
- Uses buildozer for APK generation
- Requires Android SDK and Java JDK 17
- Creates a simplified main entry point for Android compatibility
- Currently limited to non-LLM variant due to size constraints

The Android build process:
1. Sets up Android SDK and build tools
2. Creates a buildozer.spec configuration
3. Generates an Android-compatible main.py
4. Builds the APK using buildozer

## Troubleshooting

### Common Issues

1. **Missing Assets**: If photos/music directories don't exist, they're created automatically as empty directories.

2. **Large Build Size**: LLM variants will be significantly larger (100MB+) due to PyTorch and model dependencies.

3. **Android Build Failures**: Android builds are experimental and may fail due to:
   - SDL/pygame Android compatibility issues
   - Build tool version mismatches
   - APK signing requirements

4. **Windows Builds on Linux**: The GitHub Actions use native Windows runners, but local cross-compilation would require Wine.

### Build Optimization

To reduce build size:
- Use `--onefile` flag (already included)
- Consider excluding unused dependencies with `--exclude-module`
- For LLM variants, consider using smaller model variants

## Contributing

When adding new dependencies:
1. Add base dependencies to the main `dependencies` list in `pyproject.toml`
2. Add variant-specific dependencies to appropriate `optional-dependencies` sections
3. Update this README if new build requirements are introduced
4. Test builds locally before pushing

## Architecture

```
.github/workflows/          # GitHub Actions workflows
├── build-windows.yml       # Windows builds (4 variants)
├── build-linux.yml         # Linux builds (4 variants) 
├── build-android.yml       # Android build (1 variant)
└── build-all-platforms.yml # Complete build matrix + releases

legacy/                     # Main game source
├── main.py                 # Game entry point
├── pyproject.toml          # Dependencies and build config
└── [game source files]

build.sh                    # Local build helper script
```