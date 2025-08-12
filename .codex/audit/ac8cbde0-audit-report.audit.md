# Web Rewrite Audit

## Summary
Audit of tasks previously marked complete in `.codex/tasks/ac8cbde0-web-task-order.md`. Every checked item failed to meet its acceptance criteria.

## Findings
### Remove Panda3D and split repo into frontend and backend services (`e6073d6d`)
- Task demands existing game logic remain functional; backend contains no tests and `uv run pytest` collected zero items, providing no evidence of functionality【d873d2†L1-L8】

### Purge legacy GUI (`purge-old-gui`)
- Task expects a new `aspect2d` UI package, but no replacement UI exists, leaving the repository without the mandated GUI scaffold【F:.codex/tasks/done/97c19289-purge-old-gui.md†L3-L9】

### Dockerfile Review
- `Dockerfile.python` lacks Docker and Docker Compose installs and combines
  multiple setup commands in one `RUN` line, violating style guidelines【F:Dockerfile.python†L19-L29】

### Run database duplication
- Backend spawns a fresh `app.db` despite planning to reuse the encrypted `save.db`, causing duplicated state and inconsistent persistence.

## Planning Alignment
- Planning document claims the project is "ready for audit," yet the missing scaffolds and failing tasks contradict this status【F:.codex/planning/8a7d9c1e-web-game-plan.md†L6-L18】

## Remediation Plan
- New tasks added for battle/shop/rest endpoints, frontend wiring, backend tests, and Dockerfile tooling.
- Party picker and run start map display tracked for completion.
- Awaiting re-audit after these tasks are finished.

All coders must note: the lingering Panda3D reference, absent tests, and missing UI scaffold underscore an alarming lack of diligence. Every future submission will be examined with even more unforgiving scrutiny.

## Status
FAILED
