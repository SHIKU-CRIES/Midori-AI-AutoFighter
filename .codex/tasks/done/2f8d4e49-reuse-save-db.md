# Reuse existing encrypted save database (`2f8d4e49`)

## Summary
Replace the temporary `app.db` run database with the existing encrypted `save.db` so game progress and player data persist across sessions.

## Tasks
- [x] Update the backend to store runs and player data in `save.db` instead of a fresh `app.db`.
- [x] Migrate any new tables into `save.db` or adjust the schema as needed.
- [x] Update documentation and tests to reference `save.db`.

## Context
Ensures the web version preserves the existing save system instead of spawning a new database.
