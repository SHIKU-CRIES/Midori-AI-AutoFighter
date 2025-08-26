# Building Desktop Packages

Docker-based tooling in `desktop-builder/` produces native binaries for Windows and Linux.

## Usage

Run the helper scripts from the repository root:

```bash
./desktop-builder/build-windows.sh   # writes .exe to desktop-dist/windows
./desktop-builder/build-linux.sh     # writes .AppImage and .tar.gz to desktop-dist/linux
```

Each script builds a container that:

1. Compiles the Python backend with PyInstaller using `uv`.
2. Bundles the Svelte frontend with Tauri and `bun`.

Artifacts are copied to the `desktop-dist/` folder on the host.
