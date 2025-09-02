# Backend

Quart game logic server listening on port `59002`. A `SaveManager` wrapper
handles SQLCipher encryption and reads the save database at
`backend/save.db` by default. Set `AF_DB_PATH` to change the location and
provide either `AF_DB_KEY` or `AF_DB_PASSWORD` for encryption.

## Setup

```bash
cd backend
uv sync
uv run app.py
```

## LLM Loader

`backend/llms/loader.py` provides a LangChain-based loader for local models. Select a backend with `AF_LLM_MODEL`:

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- `google/gemma-3-4b-it`
- `gguf` (requires `AF_GGUF_PATH` pointing to the model file)

`load_llm()` returns an object exposing an asynchronous `generate_stream` method.

## Text-to-Speech

`backend/tts.py` wraps an optional `ChatterboxTTS` model and exposes
`generate_voice(text, audio_prompt_path=None)`. Player and foe plugins may
define a `voice_sample` pointing to a reference clip. `voice_gender` defaults to
"male", "female", or "neutral" based on the character's `char_type` but can be
overridden if needed. When dialogue is produced (e.g. in chat rooms or LLM
messages) the backend saves the generated voice to `assets/voices/<id>.wav` and
returns the relative URL in API responses.

## LRM Configuration

`GET /config/lrm` returns the current model and available `ModelName` values. `POST /config/lrm` saves a new choice in the `options` table, and `POST /config/lrm/test` runs the stored model on a stateless prompt and returns its raw reply. Chat rooms load the persisted model and forward the party context and user message, returning the LRM's response alongside existing room fields.

## Logging

The backend uses a queued, buffered logging pipeline:

- A `QueueHandler` forwards records to a `QueueListener`.
- A `TimedMemoryHandler` buffers messages and flushes them to disk roughly every 15 seconds.
- Records land in a rotating log file at `logs/backend.log`.
- A `RichHandler` remains attached for colorful console output.

The root endpoint returns a simple status payload including the configured flavor. Set `UV_EXTRA` (default `"default"`) to label this instance. Additional routes support
starting runs with a seeded 45-room map, updating the party, retrieving floor
maps, listing available player characters, returning room background images,
editing player pronouns and starting stats, and posting actions to battle, shop,
rest, or floor boss rooms. The battle endpoint runs in a background task and
supports a `snapshot` action so the frontend can poll for the latest party and
foe state while combat resolves. Room endpoints no longer advance the map
automatically—after processing a room (and any card rewards) the frontend must
call `POST /run/<run_id>/next` to move to the next node. `POST /run/start`
accepts a JSON body with `party` (1–5 owned character IDs including `player`)
and an optional `damage_type` for the player chosen from Light, Dark, Wind,
Lightning, Fire, or Ice. The response includes the validated party with passive
names. Run state is stored through the `SaveManager` in `backend/save.db` by
default; `compose.yaml` bind-mounts the `backend/` directory so the database is
persisted on the host.

Player and foe base classes assign a random damage type when none is
specified, and battles respect these preset elements without rolling new ones.

Foe balance: foes receive a 10× debuff to core stats (HP, ATK, DEF) before
room scaling is applied. This global pre‑scale adjustment happens in
`autofighter/rooms/utils._scale_stats` and lowers the minimum HP target used
by room curves accordingly, improving baseline survivability without affecting
party stats.

Battle resolution awards experience to all party members. Characters below
level 1000 receive a 10× boost to earned experience, and level-ups are synced
back to the run along with updated stats.

Victories grant gold, relic choices, upgrade items, and a small chance at pull
tickets. Gold equals a base value (5 for normal battles, 20 for bosses, 200 for
floor bosses) multiplied by the loop, a random range, and the party's rare drop
rate (`rdr`). Relic drops roll `10% × rdr` in normal fights or `50% × rdr` in
boss and floor-boss rooms. Upgrade items use the foe's element at random, cap at
4★, and their quantity scales with `rdr` with fractional amounts having a
matching chance to yield an extra item. Each fight also rolls a `10% × rdr`
chance to award a pull ticket. `rdr` boosts drop quantity and odds and, at
extreme values, can roll to upgrade relic and card star ranks (3★→4★ at 1000%
`rdr`, 4★→5★ at 1,000,000%) though success is never guaranteed.
Each defeated foe grants a temporary +55% `rdr` boost for that battle,
increasing the gold reward and number of damage-type items.

Current 5★ cards include Phantom Ally, Temporal Shield, and Reality Split.

`GET /gacha` returns the current pity counter, element-based upgrade items,
owned characters with their duplicate stacks, and whether auto-crafting is
enabled. `POST /gacha/pull` performs 1, 5, or 10 pulls, awarding 5★ or 6★
characters or 1★–4★ upgrade items keyed by element. Higher pity increases the
chance of rarer items on failed pulls. Automatic crafting of upgrade items is
disabled by default but can be toggled with `POST /gacha/auto-craft`, which
converts 125 lower-star items into one higher star and ten 4★ items into a
ticket.

`GET /players/<id>/upgrade` returns a character's current upgrade level and the
inventory of element-based items. `POST /players/<id>/upgrade` consumes
20×4★ (or 100×3★/500×2★/1000×1★) items matching the character's damage type to
raise their level, boosting core stats by 5% per rank. Upgrade levels are stored
in the `player_upgrades` table and item counts in `upgrade_items`.

`GET /player/editor` returns saved pronouns, element, and stat allocations for
the player. `PUT /player/editor` validates pronouns up to 15 characters,
ensures the chosen damage type is Light, Dark, Wind, Lightning, Fire, or Ice,
and rejects edits if a run is active or if allocations exceed the available
points. Each point boosts the matching stat by 1% (100 points doubles it).
Edits apply to new runs and to the roster view, but do not retroactively
modify an active battle.

Static assets are served from `/assets/<path>`; for example, `GET /rooms/images`
returns a JSON mapping of room types to background image URLs under `/assets/...`.

## Docker

`Dockerfile.python` installs uv, Docker, and Docker Compose in separate steps and prepares the `/.venv` directory with individual RUN commands. It exposes a `UV_EXTRA` build argument for optional extras.

```bash
docker build -f Dockerfile.python --build-arg UV_EXTRA="llm-cpu" -t autofighter-backend .
```
