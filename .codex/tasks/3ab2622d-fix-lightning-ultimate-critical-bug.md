# Fix Lady Echo Lightning Ultimate Critical Bug

**Priority**: CRITICAL  
**Origin**: Character Ability Audit (17001dd5)  
**Impact**: Game-breaking functionality loss  

## Problem Description

Lady Echo character has a critical bug where using her ultimate ability causes runtime errors because the Lightning damage type completely lacks an `ultimate()` method implementation.

**Evidence from audit**: Lightning damage type (`backend/plugins/damage_types/lightning.py`) contains `on_action()` but no `async def ultimate()` method, while all other damage types have ultimate implementations.

## Root Cause

The Lightning damage type plugin is incomplete - it's missing the core `ultimate()` method that gets called when Lady Echo (or any Lightning-type character) attempts to use their ultimate ability.

## Tasks

- Coder, implement `async def ultimate()` method in `backend/plugins/damage_types/lightning.py`
- Coder, ensure Lightning ultimate follows the same pattern as other damage types (consume ultimate charge, provide unique Lightning-themed effects)
- Coder, add appropriate Lightning-themed ultimate effects (suggestions: chain damage, speed buffs, paralysis effects)
- Coder, verify Lady Echo can successfully use ultimates after implementation
- Coder, add unit tests for Lightning ultimate functionality in `backend/tests/test_lightning_ultimate.py` (if not exists) or verify existing tests pass

## Acceptance Criteria

- [ ] Lightning damage type has properly implemented `ultimate()` method
- [ ] Lady Echo can use ultimate abilities without runtime errors  
- [ ] Lightning ultimate has thematically appropriate effects
- [ ] All existing tests continue to pass
- [ ] New or updated tests cover Lightning ultimate functionality

## Related Files

- `backend/plugins/damage_types/lightning.py` - Add ultimate method
- `backend/tests/test_lightning_ultimate.py` - Verify/add tests
- `backend/plugins/players/lady_echo.py` - Character using Lightning type

## Testing Requirements

- Manual test: Create Lady Echo character and use ultimate ability
- Unit test: Verify Lightning ultimate method executes without errors
- Integration test: Verify Lightning ultimate integrates with battle system

## Context

This fix addresses the most critical finding from the character ability audit. Lady Echo is currently unplayable for ultimate-focused gameplay due to this bug.