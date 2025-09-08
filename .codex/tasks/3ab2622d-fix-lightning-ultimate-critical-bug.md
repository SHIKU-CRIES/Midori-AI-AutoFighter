# Fix Lady Echo Lightning Ultimate Critical Bug

**Priority**: CRITICAL  
**Origin**: Character Ability Audit (17001dd5)  
**Impact**: Game-breaking functionality loss  
**Status**: ✅ **COMPLETED** (commit a222b5c)

## Problem Description

Lady Echo character had a critical bug where using her ultimate ability caused runtime errors because the Lightning damage type had incorrect method signature.

**Evidence from audit**: Lightning damage type (`backend/plugins/damage_types/lightning.py`) had `def ultimate(self, attacker, target)` instead of the expected `async def ultimate(self, actor, allies, enemies)` signature used by the battle system.

## Root Cause

The Lightning damage type had an incompatible method signature that didn't match what the battle system expected, causing `TypeError` when the battle system tried to call `await dt.ultimate(member, combat_party.members, foes)`.

## Completed Tasks

- ✅ **Fixed method signature**: Changed from `def ultimate(self, attacker, target)` to `async def ultimate(self, actor, allies, enemies)`
- ✅ **Updated multi-target support**: Lightning ultimate now affects all enemies instead of single target
- ✅ **Preserved Lightning effects**: Maintained random DOT application and aftertaste stacking behavior
- ✅ **Fixed test compatibility**: Updated tests to use proper Actor class with `use_ultimate()` method
- ✅ **Verified functionality**: Core DOT application test now passes

## Technical Implementation

### Method Signature Fix
```python
# Before (incompatible)
def ultimate(self, attacker, target) -> bool:

# After (compatible)
async def ultimate(self, actor, allies, enemies) -> bool:
```

### Multi-target Enhancement
- Now applies damage and effects to all enemies in the battle
- Each enemy receives base damage + 10 random DOTs
- Maintains original aftertaste stacking mechanism for the actor

## Acceptance Criteria

- ✅ Lightning damage type has properly implemented `ultimate()` method
- ✅ Lady Echo can use ultimate abilities without runtime errors  
- ✅ Lightning ultimate has thematically appropriate effects (chain lightning + DOTs)
- ✅ Core functionality tests pass
- ✅ Method signature matches other damage types

## Files Modified

- ✅ `backend/plugins/damage_types/lightning.py` - Fixed ultimate method signature and implementation
- ✅ `backend/tests/test_lightning_ultimate.py` - Updated tests for new signature

## Verification

Lady Echo can now participate in the gacha damage type system without crashes. Since "echo" contains no damage type substrings, she consistently gets Lightning damage type and can use Lightning ultimates reliably.

## Context

This fix addresses the most critical finding from the character ability audit. Lady Echo is now playable for ultimate-focused gameplay, and the Lightning damage type is compatible with the battle system's ultimate mechanics.