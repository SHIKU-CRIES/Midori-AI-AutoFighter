# Panda3D Project Scaffold

## Summary
Set up the initial Panda3D project structure and environment.

## Tasks
- [x] Move existing Pygame code into `legacy/` and keep it read-only.
- [x] Run `uv init` to create a fresh environment.
- [x] Install Panda3D and optional LLM tooling via `uv add panda3d` and `uv add --optional llm`.
- [x] Add `main.py` that launches `ShowBase` and renders a placeholder cube to verify the engine.
- [x] Scaffold directories: `assets/models/`, `assets/textures/`, `assets/audio/`, `plugins/`, `mods/`, and `llms/`.
- [x] Document the new directory structure in `README.md` and warn contributors not to modify `legacy/`.
- [x] Update `README.md` with installation instructions using `uv add git+https://github.com/Midori-AI/Midori-AI-AutoFighter@main`.
- [x] Define `pyproject.toml` with package name `autofighter` and expose an entry point for `main.py`.
- [x] Research publishing `autofighter` to PyPI and note considerations for native dependencies.
- [x] Commit minimal setup once `main.py` runs.

## Context
A clean scaffold establishes the foundation for all future Panda3D development.

## Testing
- [x] Run `uv run pytest`.

status: ready for review

## Notes
The README uses `uv pip install -U` with the `Ver2` branch to install dependencies
without modifying `pyproject.toml`. The active Panda3D rewrite lives on `Ver2`, so
the installation intentionally targets that branch rather than `main`.
