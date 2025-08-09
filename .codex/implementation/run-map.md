# Run Map

A minimal Panda3D scene that displays a placeholder floor map.
`RunMap` shows the text `"00: -> 01,02,03"` and switches to the
first battle room when triggered. The battle room receives a factory
for creating a new `RunMap` so returning from the fight drops the
player back onto the map. The first room spawns Luna via the player
plugin system, using the plugin's baseline stats as a placeholder foe
so combat begins immediately.

## Testing
- `uv run pytest tests/test_run_map.py::test_run_map_enters_battle` – checks map text, battle parameters, and return callback
