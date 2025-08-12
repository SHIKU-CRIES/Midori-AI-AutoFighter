# Backend

Quart game logic server listening on port `59002`. By default, the server reads
and writes the save database at `backend/save.db` (plaintext). Set `AF_DB_PATH`
to change the location and `AF_DB_KEY` if using an encrypted database.

## Setup

```bash
cd backend
uv sync
uv run app.py
```

The root endpoint returns a simple status payload. Additional routes support
starting runs, updating the party, retrieving floor maps, listing available
player characters, returning room background images, and posting actions to
battle, shop, or rest rooms. Run state is stored in `backend/save.db` by
default; `compose.yaml` bind-mounts the `backend/` directory so the database is
persisted on the host.

Static assets are served from `/assets/<path>`; for example, `GET /rooms/images`
returns a JSON mapping of room types to background image URLs under `/assets/...`.

## Docker

`Dockerfile.python` installs uv, Docker, and Docker Compose in separate steps and prepares the `/.venv` directory with individual RUN commands. It exposes a `UV_EXTRA` build argument for optional extras.

```bash
docker build -f Dockerfile.python --build-arg UV_EXTRA="llm-cpu" -t autofighter-backend .
```
