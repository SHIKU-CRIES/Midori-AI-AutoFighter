# Expose battle, shop, and rest endpoints (`b0755eeb`)

## Summary
Hook the existing battle, shop, and rest room logic into the Quart backend with dedicated endpoints so the web UI can drive core gameplay.

## Tasks
- [x] Add Quart routes for battle, shop, and rest rooms.
- [x] Reuse current game logic and persist run state in `save.db`.
- [x] Document the API contract in `.codex/implementation`.

## Context
Enables the frontend to interact with core gameplay rooms.
