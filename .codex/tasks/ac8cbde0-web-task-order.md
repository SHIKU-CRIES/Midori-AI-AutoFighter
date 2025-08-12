# Web Rewrite Task Order

## Summary
Ordered steps for moving Midori AI AutoFighter to a Svelte frontend and a Python Quart backend. Reminder: list only task titles and file names—open each task file for details. (ready for audit)

- Read `.codex/planning/8a7d9c1e-web-game-plan.md` before starting or auditing any task.
- Coordinate with the reviewer or Task Master before marking a task complete.
- Keep `myunderstanding.md` up to date with the game's flow.

## Tasks
### To Do
- [ ] [Wire Svelte UI to room endpoints](e1cfb77c-frontend-room-wiring.md) (`e1cfb77c`)
- [ ] [Add backend tests for run and rooms](5cc4df14-backend-tests.md) (`5cc4df14`)
- [ ] [Fix backend Dockerfile tooling](8f1bafea-dockerfile-tooling.md) (`8f1bafea`)

### Completed
- [x] [Reuse existing encrypted save database](done/2f8d4e49-reuse-save-db.md) (`2f8d4e49`)
- [x] [Make web build playable](done/7d79b17b-playable-flow.md) (`7d79b17b`)
- [x] [Party picker](done/f9c45e2e-party-picker.md) (`f9c45e2e`)
- [x] [Responsive layout for Svelte UI](done/33c77b60-responsive-layout.md) (`33c77b60`)
- [x] [Expose battle, shop, and rest endpoints](done/b0755eeb-room-endpoints.md) (`b0755eeb`)
- [x] [Add Docker Compose profiles for LLM extras](e09f282f-compose-llm-profiles.md) (`e09f282f`)
- [x] [Fix backend Dockerfile](done/34f8a5b0-fix-backend-dockerfile.md) (`34f8a5b0`)
- [x] [Remove Panda3D and split repo into frontend and backend services](done/e6073d6d-remove-panda3d-structure.md) (`e6073d6d`)
- [x] [Purge legacy GUI](done/97c19289-purge-old-gui.md) (`purge-old-gui`)
- [x] [Scaffold Svelte frontend](done/bcaaad20-svelte-frontend-scaffold.md) (`bcaaad20`)
- [x] [Scaffold Quart backend](done/1faf53ba-quart-backend-scaffold.md) (`1faf53ba`)
- [x] [Run start and map display](done/dc3d4f2e-run-start-map-display.md) (`dc3d4f2e`)

## Context
Switching from Panda3D to a web-based GUI with a Quart backend managed via Docker Compose.
