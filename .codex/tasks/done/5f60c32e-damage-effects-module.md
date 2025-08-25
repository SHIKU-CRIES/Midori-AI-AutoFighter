# Damage Effects Module

## Please Review
Confirm factory mappings cover all elements and support future relic or card hooks.
## Summary
Introduce a dedicated `damage_effects` module so players and foes load damage-type effects (DoTs/HoTs) without circular imports. This will also let relics and cards hook in to tweak certain DoTs.

## Tasks
- Create a `damage_effects` module under `backend/plugins/` that maps each damage type to its DoT and HoT effect factories.
- Refactor damage type plugins to fetch their effects from this module instead of importing DoT/HoT plugins directly.
- Ensure players and foes initialize damage types and apply effects through `damage_effects` to avoid circular imports.
- Adjust `autofighter/effects.py` or related modules to integrate the new system.
- Document the system in `.codex/instructions/damage-healing.md` and any relevant README sections.
- Add tests validating DoT/HoT application via `damage_effects` and update existing tests as needed.

## Context
Damage type plugins currently import specific DoT or HoT modules inside their `create_dot` methods, creating fragile circular dependencies. A central module will decouple elements from their effects and offer unified control.

## Testing
- `./run-tests.sh` (skip `uv run pytest`; it currently crashes)
