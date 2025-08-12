# Web Rewrite Audit

## Summary
Audit of tasks marked complete in `.codex/tasks/ac8cbde0-web-task-order.md`. None met their acceptance criteria.

## Findings
### Reuse existing encrypted save database (`2f8d4e49`)
- Repository ships without the promised `save.db`, so the backend creates a fresh database each run【bf54e5†L1-L2】
- `compose.yaml` lacks any volume or environment configuration to mount a persistent save file【F:compose.yaml†L1-L13】

### Make web build playable (`7d79b17b`)
- Player plugins still import `game.actors`, causing the backend to crash with `ModuleNotFoundError` on startup【F:backend/plugins/players/ally.py†L1-L14】
- Frontend container has no command or working directory, leaving the service dead on launch【F:Dockerfile.js†L1-L30】

### Party picker (`f9c45e2e`)
- Task demands pre-run setup and character upgrades, yet the component only toggles selections; no upgrade flow exists【F:.codex/tasks/done/f9c45e2e-party-picker.md†L5-L12】【F:frontend/src/lib/PartyPicker.svelte†L13-L55】
- Planning still flags the party picker as unfinished, contradicting the completion claim【F:.codex/planning/8a7d9c1e-web-game-plan.md†L15-L19】

### Responsive layout for Svelte UI (`33c77b60`)
- Tests merely assert width mappings and never verify panel visibility, failing the acceptance criteria for layout behavior【F:frontend/tests/layout.test.js†L1-L16】

### Expose battle, shop, and rest endpoints (`b0755eeb`)
- Endpoints return stub JSON and ignore existing game logic, directly contradicting the task's requirement to reuse current systems【F:backend/app.py†L111-L126】【F:.codex/implementation/room-endpoints.md†L1-L14】

### Add Docker Compose profiles for LLM extras (`e09f282f`)
- Each profile inherits the base backend's port mapping, so enabling a profile collides on host port `59002`【F:compose.yaml†L8-L22】

### Fix backend Dockerfile (`34f8a5b0`)
- Dockerfile still references an undefined `USERNAME` variable, risking build failures on images lacking that environment value【F:Dockerfile.python†L24-L30】

### Remove Panda3D and split repo into frontend and backend services (`e6073d6d`)
- Numerous docs still reference Panda3D features like the `messenger`, proving the cleanup was never finished【F:.codex/implementation/event-bus.md†L1-L5】

### Purge legacy GUI (`purge-old-gui`)
- Task promises a fresh `aspect2d` UI scaffold, yet no such package exists anywhere in the repository【F:.codex/tasks/done/97c19289-purge-old-gui.md†L3-L9】

### Scaffold Svelte frontend (`bcaaad20`)
- Missing `CMD`, `COPY`, and `WORKDIR` lines in the Dockerfile prevent the frontend container from running at all【F:Dockerfile.js†L1-L30】

### Scaffold Quart backend (`1faf53ba`)
- Backend startup depends on non-existent `game` modules, so the supposed scaffold is non-functional【F:backend/plugins/players/ally.py†L1-L14】
- Required endpoint for room images is absent from `app.py`【F:.codex/tasks/done/1faf53ba-quart-backend-scaffold.md†L5-L12】【F:backend/app.py†L51-L134】

### Run start and map display (`dc3d4f2e`)
- Test only checks for a literal string in the component file, offering no proof that map buttons render or function【F:frontend/tests/runmap.test.js†L5-L9】
- Planning explicitly lists this feature as unfinished【F:.codex/planning/8a7d9c1e-web-game-plan.md†L15-L19】

## Status
FAILED

Coders: every unchecked box and hollow test in this audit screams negligence. The missing database, crashing backend, inert frontend container, and lingering Panda3D baggage prove that corners were cut at every turn. Tighten up now; the next audit will be even harsher, and no excuse will survive.
