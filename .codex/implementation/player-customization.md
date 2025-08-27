# Player Editor

`PlayerEditor` now connects to backend endpoints and is launched from the main
menu's **Edit** button or automatically before a run, so players can set custom
pronouns up to 15 characters, pick a starting damage type—Light, Dark, Wind,
Lightning, Fire, or Ice—and allocate stat points before starting a run.

- Players start with 100 base points and may gain bonus points from owning 100 of each damage type's 4★ upgrade items.
- Sliders for HP, Attack, and Defense clamp so the sum never exceeds the available pool.
- Each point grants a 1% multiplier to the chosen stat, doubling it at 100 points.
- A label displays remaining points.
- The Confirm button is disabled until the 100 base points are spent. Bonus points are optional and unspent amounts stay in the inventory.
- Attempting to spend more points than covered by 4★ items shows a warning and prevents saving. Backend `PUT /player/editor`
  also enforces the 100-point cap and rejects edits while a run is active.

## Implementation Architecture

Player customization is applied during character instantiation rather than as temporary modifiers to prevent stat accumulation bugs:

### Base Stat Application
- The `Player` class `__post_init__` method applies customization directly to base stats (`hp`, `max_hp`, `atk`, `defense`) during object creation
- Customization values are read from the `options` table in the database (`player_stats` key)
- Each customization point provides a 1% multiplier applied once during instantiation
- This ensures stats remain stable across save/load cycles

### Backwards Compatibility  
- The `_apply_player_customization()` function now skips the base player (id="player") since customization is built-in
- Saved effects from older versions are still handled for backwards compatibility
- Old custom multiplier data is automatically removed from save files to prevent conflicts

### Save System Integration
- Player saves no longer store custom multipliers since customization is now permanent
- Only damage type and other non-stat data are preserved across save/load cycles
- This prevents the exponential stat growth that occurred when mods were reapplied on each load

## Persistence notes

Earlier builds lost stat allocations because the editor saved `damage` and
string-valued stats, causing the backend to ignore the update and return zeros
on the next load. The component now dispatches numeric `hp`, `attack`, and
`defense` values alongside a `damageType` field that the page converts to the
API's `damage_type` key, so edited stats persist after saving and reloading.

The current implementation permanently applies customization during player instantiation, ensuring consistent stats while maintaining all editor functionality.
