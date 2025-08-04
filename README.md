# Midori AI AutoFighter

This repository is the starting point for a Panda3D-based rewrite of Midori AI AutoFighter.
The previous Pygame codebase lives in `legacy/` and must remain unmodified.

## Directory Structure

```
assets/
  audio/
  models/
  textures/
plugins/
mods/
llms/
legacy/
```

## Setup

1. Install [uv](https://github.com/astral-sh/uv).
2. Create a virtual environment and install the project:

   ```bash
   uv venv --python python3.12
   uv pip install -U git+https://github.com/Midori-AI-OSS/Midori-AI-AutoFighter@Ver2
   ```
   The `uv pip install -U` command installs the latest dependencies without editing
   `pyproject.toml`. The `Ver2` branch hosts the active Panda3D rewrite, so the
   installation targets that branch rather than `main`.
3. Run the placeholder application:

   ```bash
   uv run autofighter
   ```

## Publishing

The package will be published to PyPI as `autofighter`. Panda3D provides platform-specific
wheels, so native dependencies must be considered when distributing builds.

## Testing

Run the test suite before submitting changes:

```bash
uv run pytest
```

## Plugins

Custom modules live in `plugins/` or `mods/`. See `.codex/instructions/plugin-system.md` for details on creating new plugins.

## Playable Characters

The roster in `plugins/players/` currently includes:

- Ally
- Becca
- Bubbles
- Carly
- Chibi
- Graygray
- Hilander
- Kboshi
- Lady Darkness
- Lady Echo
- Lady Fire and Ice
- Lady Light
- Lady of Fire
- Luna
- Mezzy
- Mimic
