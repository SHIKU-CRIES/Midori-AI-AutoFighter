# Fix Random Ultimate Assignment System

**Priority**: HIGH  
**Origin**: Character Ability Audit (17001dd5)  
**Impact**: Major gameplay design flaw affecting 8 characters  

## Problem Description

Eight characters (Ally, Becca, Bubbles, Chibi, Graygray, Hilander, Mezzy, Mimic) currently receive completely random ultimate abilities each time they are instantiated, making character behavior unpredictable and inconsistent with game design.

**Root Cause**: The `get_damage_type()` function in `backend/plugins/damage_types/__init__.py` falls back to `random_damage_type()` for character names that don't match any special cases or substrings.

## Impact Analysis

- Characters can randomly receive any of 6 ultimate types (Light/Dark/Wind/Lightning/Fire/Ice)
- Completely unpredictable gameplay experience
- Impossible to balance characters or create consistent strategies
- Lightning selection would cause crashes (see related Lightning ultimate bug)
- Players cannot rely on character abilities

## Tasks

### Design Decision Required
- Task Master, determine whether these 8 characters should:
  - A) Have unique character-specific ultimate implementations
  - B) Have fixed assignments to existing damage types (e.g., Ally→Fire, Becca→Ice)
  - C) Continue with random but document this as intended behavior

### Implementation Tasks (after design decision)
- Coder, modify `get_damage_type()` function to provide explicit mapping for these 8 characters
- Coder, implement character-specific damage types if option A is chosen
- Coder, update character plugin files to reflect chosen ultimate assignments
- Coder, add unit tests verifying consistent ultimate assignment for each character
- Coder, update documentation to reflect actual ultimate behavior

### Documentation Tasks
- Coder, update `.codex/docs/character-passives.md` with correct ultimate information
- Coder, update character ability compilation to reflect new assignments

## Current Affected Characters

| Character | Current Behavior | Suggested Assignment |
|-----------|------------------|---------------------|
| Ally | Random | Fire (matches twin dagger aggressive style) |
| Becca | Random | Wind (matches variable nature) |
| Bubbles | Random | Ice (matches bubble/freeze theme) |
| Chibi | Random | Lightning (matches energetic small character) |
| Graygray | Random | Dark (matches counter/defensive style) |
| Hilander | Random | Fire (matches critical/ferment explosive theme) |
| Mezzy | Random | Dark (matches gluttony/drain mechanics) |
| Mimic | Random | Generic (matches adaptive/copying nature) |

## Acceptance Criteria

- [ ] All 8 characters have predictable, consistent ultimate assignments
- [ ] Ultimate assignments match character themes and gameplay styles
- [ ] No more random ultimate selection for any character
- [ ] Documentation accurately reflects ultimate assignments
- [ ] All tests pass with new assignments

## Related Files

- `backend/plugins/damage_types/__init__.py` - get_damage_type function
- `backend/plugins/players/` - All affected character files
- `.codex/docs/character-passives.md` - Documentation updates
- Test files for ultimate functionality

## Dependencies

This task should be completed after the Lightning ultimate bug fix to ensure all ultimate types are functional.

## Testing Requirements

- Unit tests verifying each character gets the same ultimate type consistently
- Integration tests verifying ultimate functionality for all assignments
- Manual testing of character ultimate usage in battles