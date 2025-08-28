# Midori AI AutoFighter

Midori AI AutoFighter is being rebuilt as a web application. A Svelte frontend
communicates with a Python Quart backend, and Docker Compose orchestrates both
services. The legacy Pygame prototype lives in `legacy/` and remains untouched.

## Directory Structure

```
frontend/   # Svelte frontend
backend/    # Quart backend and game logic
legacy/     # Previous Pygame version (read-only)
```

## Standalone Builds

The repository includes automated GitHub Actions workflows to build standalone game executables for multiple platforms. See [BUILD.md](BUILD.md) for complete documentation.

### Available Builds
- **Windows** (4 variants): non-llm, llm-cpu, llm-cuda, llm-amd
- **Linux** (4 variants): non-llm, llm-cpu, llm-cuda, llm-amd  
- **Android** (1 variant): non-llm

### Quick Local Build
```bash
# Build for current platform
./build.sh

# Build specific variant
./build.sh llm-cpu
```

Builds are automatically created on every push and releases are generated for version tags. Download the latest builds from the [Releases page](../../releases).

## Setup

1. Install [uv](https://github.com/astral-sh/uv) and
   [bun](https://bun.sh/).

   > **Reminder:** Keep the `version` fields in [`backend/pyproject.toml`](backend/pyproject.toml) and [`frontend/package.json`](frontend/package.json) in sync with the repository `folderhash`; update them with every change.
2. Start both services with Docker Compose (bind-mounted source):

```bash
docker compose up --build frontend backend
```

Compose bind-mounts `frontend/` and `backend/` into the containers. The backend
stores its database at `backend/save.db` by default (override with
`AF_DB_PATH`). Provide `AF_DB_KEY` or `AF_DB_PASSWORD` for encryption via the
`SaveManager`. The Svelte dev server listens on `59001` and the Quart backend
on `59002`.

### Dev Workflow
- Code changes are reflected immediately since source is bind-mounted into the containers.
- Frontend entrypoint runs `bun install` if `node_modules/` is missing, then starts the dev server.
- Backend entrypoint runs `uv sync` (respects `UV_EXTRA`) and launches the Quart app with `uv run app.py`.
- The backend serves static assets under `/assets/*` and exposes `GET /rooms/images` with room background URLs.

### Optional LLM Dependencies

Install extras to experiment with local language models. Each extra bundles
LangChain, Transformers, and a matching PyTorch build:

```bash
uv sync --extra llm-cuda  # NVIDIA GPUs (CUDA drivers required)
uv sync --extra llm-amd   # AMD/Intel GPUs (ROCm or oneAPI)
uv sync --extra llm-cpu   # CPU-only
```

Selecting the correct extra ensures hardware acceleration when available. These
packages are optional; the core game runs without them.

#### LLM Features

When LLM dependencies are installed, the application provides:

- **Model Testing**: Test LLM models through the settings menu (async-friendly to prevent backend lockup)
- **Chat Rooms**: AI-powered chat interactions with party members
- **Player/Foe Memory**: Persistent conversation memory using ChromaDB vector storage
- **Centralized Management**: Single torch availability check on startup with consistent error handling

All LLM operations are asynchronous and won't block the game interface. Models are loaded in background threads and configured with proper generation parameters to minimize warnings.

The backend exposes `/config/lrm` to retrieve and set the active LRM. A companion `/config/lrm/test` endpoint runs the chosen model on a stateless prompt. The frontend settings menu surfaces these options so players can switch between DeepSeek, Gemma, and GGUF models and test responses.

3. Run the backend directly (without Docker):

```bash
cd backend
uv run app.py
```

The server uses `AF_DB_PATH` for the save database (default
`backend/save.db`). Supply `AF_DB_KEY` or `AF_DB_PASSWORD` to open the
encrypted database; without either it opens plaintext.

4. Install the latest build into another project:

```bash
uv add git+https://github.com/Midori-AI/Midori-AI-AutoFighter@main
```

### Docker Compose LLM Profiles

Enable optional LLM dependencies with Compose profiles. All profiles reuse port
`59002` and intentionally conflict with the standard backend—only one profile
should run at a time:

```bash
docker compose --profile llm-cuda up --build   # backend on 59002
docker compose --profile llm-amd up --build    # backend on 59002
docker compose --profile llm-cpu up --build    # backend on 59002
```

## Responsive Layout

The Svelte frontend targets three breakpoints:

 - **Desktop** – displays the party picker, player editor, and icon-based floor
  map around the active menu so most information is visible at once.
- **Tablet** – shows two panels side by side when space permits.
- **Phone** – focuses on a single menu at a time for clarity on small screens.

The interface adapts automatically based on viewport width.

## Publishing

Docker images for both services will be published to Docker Hub. Native
dependencies are handled inside the images, so no manual wheel management is
required.

## Package Installation

Install prebuilt packages when available:

- **Flatpak**

  ```bash
  flatpak install org.midori.ai.autofighter
  ```

- **Arch Linux (AUR)**

  ```bash
  yay -S autofighter-git
  ```

- **Debian/Ubuntu**

  ```bash
  sudo apt install ./autofighter.deb
  ```

## Desktop Builds

Scripts under `build/desktop/` package the app for Windows and Linux. Each
script builds a Docker image that compiles the Python backend with PyInstaller
and bundles the Svelte frontend with Tauri.

```bash
./build/desktop/build-windows.sh   # outputs .exe to desktop-dist/windows
./build/desktop/build-linux.sh     # outputs .AppImage and .tar.gz to desktop-dist/linux
```

See `.codex/instructions/building-desktop.md` for details.

## Testing

Run the test suites before submitting changes with the helper script:

```bash
./run-tests.sh
```

The script prepares the environments by creating and syncing a Python virtual
environment in `backend/` (`uv venv && uv sync`) and installing frontend
dependencies with `bun install` in `frontend/`. It then runs each backend
`pytest` module via `uv` and executes the frontend `bun test` files. Each test
is given a 15-second timeout, and all tests are run regardless of failures. The
script prints a summary of any failing or timed-out tests and exits with the
first non-zero status code encountered.

## Loot and Rare Drop Rate

Battles award gold, relic choices, upgrade items, and occasionally pull tickets.
Gold equals a base value of 5/20/200 for normal, boss, and floor-boss rooms,
multiplied by the loop, a random range, and the party's rare drop rate (`rdr`).
Relics drop with `10% × rdr` odds in normal fights or `50% × rdr` in boss rooms.
Upgrade items use the foe's element, cap at 4★, and their quantity scales with
`rdr`—fractions have a matching chance to grant an extra item. Each battle also
rolls a `10% × rdr` chance for a pull ticket. `rdr` improves drop quantity and
odds and can even upgrade relic or card star ranks with lucky rolls at extreme
values: climbing from 3★ to 4★ requires 1000% `rdr`, while 5★ demands a
colossal 1,000,000%.

## Plugins

The game auto-discovers classes under `plugins/` and `mods/` by `plugin_type`
and wires them to a shared event bus. See
`.codex/implementation/plugin-system.md` for loader details and examples.
Player and foe plugins also expose `prompt` and `about` strings with
placeholder text for future character customization.

## Player Creator

Use the in-game editor to pick a body and hair style, choose a hair color and
accessory, and distribute 100 stat points. Spending 100 of each damage type's
4★ upgrade items grants one extra stat point. The result is stored in the
encrypted `save.db` database for new runs.

## Stat Screen

View grouped stats and status effects. The display refreshes every few frames
and supports plugin-provided lines. Categories cover core, offense, defense,
vitality, advanced data, and status lists for passives, DoTs, HoTs, and damage
types.

## Damage and Healing Effects

Elemental damage types hook into attacks. The `plugins/damage_effects.py` module maps each element to its DoT and HoT factories so plugins can request effects without importing one another:

- **[Fire](backend/plugins/damage_types/fire.py)** – Damage scales with missing HP and applies [Blazing Torment](backend/plugins/dots/blazing_torment.py), a stackable DoT that ticks again when the target acts.
- **[Ice](backend/plugins/damage_types/ice.py)** – Inflicts [Frozen Wound](backend/plugins/dots/frozen_wound.py), which lowers the victim's actions per turn and adds a 1% miss chance per stack. Some skills use [Cold Wound](backend/plugins/dots/cold_wound.py) with a five-stack limit.
- **[Lightning](backend/plugins/damage_types/lightning.py)** – Pops every active DoT on hit, dealing 25% of each effect's damage immediately, and applies [Charged Decay](backend/plugins/dots/charged_decay.py), which stuns on its final tick.
- **[Wind](backend/plugins/damage_types/wind.py)** – After the first hit, repeats the strike on each remaining foe and rolls [Gale Erosion](backend/plugins/dots/gale_erosion.py) on every target, shaving Mitigation each tick.
- **[Light](backend/plugins/damage_types/light.py)** – Creates [Celestial Atrophy](backend/plugins/dots/celestial_atrophy.py) and grants allies [Radiant Regeneration](backend/plugins/hots/radiant_regeneration.py) every action. If an ally falls below 25% HP, the attack is replaced with a direct heal.
- **[Dark](backend/plugins/damage_types/dark.py)** – Spreads [Abyssal Corruption](backend/plugins/dots/abyssal_corruption.py) and adds a permanent [Shadow Siphon](backend/plugins/dots/shadow_siphon.py) to each party member every turn, draining 5% max HP per tick while feeding attack and defense back to the caster.

DoT and HoT plugins manage ongoing damage or recovery. Supported DoTs include
[Bleed](backend/plugins/dots/bleed.py),
[Poison](backend/plugins/dots/poison.py),
[Celestial Atrophy](backend/plugins/dots/celestial_atrophy.py),
[Abyssal Corruption](backend/plugins/dots/abyssal_corruption.py),
[Abyssal Weakness](backend/plugins/dots/abyssal_weakness.py),
[Gale Erosion](backend/plugins/dots/gale_erosion.py),
[Charged Decay](backend/plugins/dots/charged_decay.py),
[Frozen Wound](backend/plugins/dots/frozen_wound.py),
[Blazing Torment](backend/plugins/dots/blazing_torment.py),
[Cold Wound](backend/plugins/dots/cold_wound.py),
[Twilight Decay](backend/plugins/dots/twilight_decay.py),
[Impact Echo](backend/plugins/dots/impact_echo.py),
and [Shadow Siphon](backend/plugins/dots/shadow_siphon.py).
HoTs cover [Regeneration](backend/plugins/hots/regeneration.py),
[Player Echo](backend/plugins/hots/player_echo.py),
[Player Heal](backend/plugins/hots/player_heal.py),
and [Radiant Regeneration](backend/plugins/hots/radiant_regeneration.py).
Foes regenerate at one hundredth the player rate to prevent drawn-out encounters.

## Battle Room

Start a run in a battle scene that renders placeholder models, triggers party
passives, and runs event-driven stat-based attacks against a `Slime` or any
non-party player character scaled by floor, room, Pressure level, and loop
count. Foes are procedurally named by prefixing a themed adjective plugin to a
player name. Adjective plugins are auto-discovered from files in
`plugins/themedadj`, allowing new adjectives to be added without modifying
package code. Each adjective applies its stat tweaks through a persistent
`StatModifier` buff so base values are restored when the foe falls. Foes inherit
from a dedicated `FoeBase` that mirrors player stats
but starts with negligible mitigation and vitality;
the default `Slime` reduces them by 90% on spawn, while player-derived foes gain
`FoeBase` behaviors like turn-based regeneration. The scene shows floating
damage numbers and status icons and flashes
red and blue with an Enraged buff after 100 turns (500 for floor bosses). Each
victory presents three unused cards of the appropriate star rank. Selecting one
adds it to the party, and card and relic bonuses are applied at the start of the
next battle.

Parties also track a rare drop rate (`rdr`) that boosts relic drops, gold
rewards, upgrade item counts, and pull ticket chances. At extreme values it can
roll to raise relic and card star ranks (3★→4★ at 1000% `rdr`, 4★→5★ at
1,000,000%), but even huge `rdr` never guarantees success. The 3★ Greed Engine
relic raises `rdr` while draining HP each turn.

Defeated foes grant experience to every party member. Characters below level
1000 receive a 10× boost to experience gained so early levels advance quickly.
Level-ups apply immediately and sync back to the run along with remaining HP.

## Rest Room

Pull for new characters, craft items, or rearrange the party before continuing a
run. Map generation ensures at least two rest rooms per floor, and any recruits
join the roster immediately.

## Shop Room

Entering a shop heals the party by 5% of its combined max HP. Buy upgrade items
or cards with star ratings. Inventory scales by floor, purchases add items to
your inventory and disable the button, class-level tracking guarantees at least
two shops per floor, and gold can reroll the current stock. Gold prices per star
rank, pressure-based cost scaling, and reroll rules are documented in
[`./.codex/implementation/shop-room.md`](.codex/implementation/shop-room.md).

## Event and Chat Rooms

Event Rooms offer text-based encounters with selectable options that use seeded
randomness to modify stats or inventory. Chat Rooms, available only when the LLM
profiles are installed, let players send a single message to an LLM character,
track usage per floor, and do not count toward the floor's room limit; only six
chats may occur on each floor.

## Per-instance Memory

Each player and foe instance now maintains its own LangChain ChromaDB memory.
Use `send_lrm_message` to converse with the LRM and `receive_lrm_message` to
record incoming replies. Histories are scoped to the current run so dialogs stay
isolated between combatants.

## Map Generation

New runs begin by selecting up to four owned allies in a party picker before the
map appears. Runs then progress through 45-room floors built by a seeded
`MapGenerator`. Each floor includes at least two shops and two rest rooms,
battle nodes marked as `battle-weak` or `battle-normal`, and ends in a
`battle-boss-floor`. Chat scenes may appear after battles only when the LLM
profiles are installed and do not affect room count. The frontend shows these
nodes as stained-glass buttons with `lucide-svelte` icons for battles, shops,
rests, and bosses.

## Playable Characters

The roster in `plugins/players/` currently includes and each entry lists its
`CharacterType`. All players start with 1000 HP, 100 attack, 50 defense, a 5%
crit rate, 2× crit damage, 1% effect hit rate, 100 mitigation, 0 dodge, and 1
in all other stats. Listed damage types use the classic naming from the
Pygame version:

- Ally (B, random damage type)
- Becca (B, random damage type)
- Bubbles (A, random damage type)
- Carly (B, Light) – converts attack growth into defense
- Chibi (A, Lightning)
- Graygray (B, random damage type)
- Hilander (A, random damage type)
- Kboshi (A, random damage type)
- Lady Darkness (B, Dark)
- Lady Echo (B, Lightning)
- Lady Fire and Ice (B, Fire or Ice)
- Lady Light (B, Light)
- Lady of Fire (B, Fire)
- Luna (B, Generic)
- Mezzy (B, random damage type)
- Mimic (C, random damage type)
- Player (C, chosen damage type)

Characters with a "random damage type" roll their element on first load and
reuse that result in future sessions.
