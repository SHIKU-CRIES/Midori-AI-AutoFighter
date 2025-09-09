# Character Ability Audit - Discrepancy Analysis

**Audit ID**: `17001dd5-discrepancy-analysis`  
**Persona**: Coder  
**Date**: Generated during character ability audit task  
**Scope**: Comprehensive documentation of discrepancies between documented and actual behavior

## Executive Summary

This document catalogs all discrepancies discovered between documented character abilities and their actual implementation. The findings reveal **fundamental misunderstandings** in the ultimate system documentation and **one critical functional bug** that breaks Lady Echo's ultimate usage.

## Critical Discrepancies

### 1. **Lady Echo Ultimate - CRITICAL BUG**

**Documented Behavior**: Lady Echo should have Lightning-based ultimate abilities
**Actual Behavior**: Lightning damage type (`backend/plugins/damage_types/lightning.py`) has NO `ultimate` method implementation
**Impact**: 
- Lady Echo cannot use ultimates without causing runtime errors
- Breaks core gameplay mechanic for this character
- Affects any future characters using Lightning damage type

**Evidence**:
```python
# lightning.py contains on_action() but NO ultimate() method
# All other damage types have async def ultimate() methods
```

**Severity**: CRITICAL - Functional game-breaking bug

### 2. **8 Characters Have Completely Random Ultimates - HIGH SEVERITY**

**Characters Affected**: Ally, Becca, Bubbles, Ixia, Graygray, Hilander, Mezzy, Mimic

**Documented Behavior**: Each character should have unique "custom damage type" ultimates
**Actual Behavior**: Characters get random ultimates each time they're instantiated
**Root Cause**: `get_damage_type()` falls back to `random_damage_type()` for unmatched character names

**Evidence**:
```python
# From plugins/damage_types/__init__.py
def get_damage_type(name: str) -> DamageTypeBase:
    # ... special cases for luna, kboshi ...
    matches = [dtype for dtype in ALL_DAMAGE_TYPES if dtype.lower() in lowered]
    if matches:
        return _load_cls(choice(matches))()
    return random_damage_type()  # 8 characters end up here
```

**Impact**:
- Characters can have any of 6 different ultimates (Light/Dark/Wind/Lightning/Fire/Ice)
- Completely unpredictable gameplay
- Lightning selection would cause runtime errors (see issue #1)
- Inconsistent with character design and player expectations

**Severity**: HIGH - Fundamentally broken character design

### 3. **Lady Fire and Ice Inconsistent Ultimate - HIGH SEVERITY**

**Documented Behavior**: Should have unique dual-element "custom damage type" ultimate
**Actual Behavior**: Randomly receives either Fire ultimate OR Ice ultimate due to substring matching
**Root Cause**: Both "fire" and "ice" substrings match, `choice()` randomly picks one

**Evidence**:
```python
# "lady_fire_and_ice" contains both "fire" and "ice" substrings
matches = ["Fire", "Ice"]  # Both match
return _load_cls(choice(matches))()  # Random selection
```

**Impact**:
- Character behavior changes between game sessions
- Sometimes gets Fire ultimate (AoE damage + DoT)
- Sometimes gets Ice ultimate (6-hit ramping damage)
- Player cannot predict character capabilities

**Severity**: HIGH - Inconsistent character mechanics

### 4. **Kboshi and Luna Undocumented Ultimate Behavior - MEDIUM SEVERITY**

#### Kboshi
**Documented Behavior**: Listed as having "custom Kboshi damage type"
**Actual Behavior**: Uses Dark damage type and Dark ultimate
**Evidence**: `if "kboshi" in lowered: return _load_cls("Dark")()`

#### Luna
**Documented Behavior**: Listed as having "custom Luna damage type"  
**Actual Behavior**: Uses Generic damage type and Generic ultimate
**Evidence**: `if "luna" in lowered: return _load_cls("Generic")()`

**Impact**: Documentation is incorrect but functionality exists
**Severity**: MEDIUM - Misleading documentation but functional

### 5. **Missing Gacha Rarity Fields - MEDIUM SEVERITY**

**Characters Affected**: Luna, Lady of Fire
**Issue**: Character plugins missing `gacha_rarity` field
**Impact**: 
- May cause issues in gacha system display/logic
- Inconsistent character metadata
- Could lead to runtime errors in gacha operations

**Evidence**:
```python
# luna.py and lady_of_fire.py lack gacha_rarity = X line
# All other characters have this field
```

**Severity**: MEDIUM - Functional gap in character metadata

### 6. **Orphaned Passive Implementations - LOW SEVERITY**

**Unused Passives**: `advanced_combat_synergy`, `room_heal`
**Issue**: Fully implemented passives with no character assignments
**Impact**: 
- Code bloat
- Potential confusion
- Wasted development effort

**Evidence**: No character in `backend/plugins/players/` references these passive IDs
**Severity**: LOW - No functional impact

## Documentation vs Reality Matrix

### Ultimate System Discrepancies

| Character | Documented Ultimate | Actual Ultimate | Discrepancy Type |
|-----------|-------------------|----------------|------------------|
| Lady Echo | Lightning (custom) | **BROKEN** | Critical Bug |
| Ally | Custom Ally | Random (6 types) | Major Design Flaw |
| Becca | Custom Becca | Random (6 types) | Major Design Flaw |
| Bubbles | Custom Bubbles | Random (6 types) | Major Design Flaw |
| Ixia | Custom Ixia | Random (6 types) | Major Design Flaw |
| Graygray | Custom Graygray | Random (6 types) | Major Design Flaw |
| Hilander | Custom Hilander | Random (6 types) | Major Design Flaw |
| Mezzy | Custom Mezzy | Random (6 types) | Major Design Flaw |
| Mimic | Custom Mimic | Random (6 types) | Major Design Flaw |
| Lady Fire and Ice | Custom Dual | Fire OR Ice (random) | Inconsistent Behavior |
| Kboshi | Custom Kboshi | Dark | Undocumented Reality |
| Luna | Custom Luna | Generic | Undocumented Reality |
| Carly | Light | Light | ✅ Correct |
| Lady Light | Light | Light | ✅ Correct |
| Lady Darkness | Dark | Dark | ✅ Correct |
| Lady of Fire | Fire | Fire | ✅ Correct |
| Player | Fire (customizable) | Fire (default) | ✅ Correct |

### Passive System Discrepancies

| Character | Documented Passive | Actual Passive | Status |
|-----------|-------------------|----------------|---------|
| All 18 characters | Various | Various | ✅ All correct |
| N/A | N/A | `advanced_combat_synergy` | Orphaned |
| N/A | N/A | `room_heal` | Orphaned |

## Root Cause Analysis

### Ultimate System Design Flaw
The fundamental issue is in the `get_damage_type()` function design:

1. **Overly Generic Approach**: Attempts to infer damage type from character name rather than explicit mapping
2. **Fallback Randomness**: Random selection for unmatched names creates unpredictable behavior
3. **Substring Matching**: Multiple matches (like "fire" and "ice") cause inconsistent selection
4. **Missing Implementation**: Lightning ultimate never implemented but is part of random selection pool

### Documentation Assumptions
The documentation incorrectly assumes that:
1. Characters with `get_damage_type("CharacterName")` get unique damage types
2. Custom damage types are implemented for each character
3. Ultimate behavior is predictable and character-specific

### Reality
1. Only explicit special cases (Luna→Generic, Kboshi→Dark) are predictable
2. Most characters get random or substring-matched standard damage types
3. One standard damage type (Lightning) is broken

## Impact on Gameplay

### Player Experience Issues
1. **Broken Functionality**: Lady Echo ultimates cause crashes
2. **Unpredictable Characters**: 8 characters have different ultimates each game
3. **Inconsistent Mechanics**: Lady Fire and Ice behavior varies randomly
4. **Misleading Expectations**: Documentation doesn't match reality

### Development Issues
1. **Testing Complexity**: Random ultimates make character testing difficult
2. **Bug Reports**: Players may report "inconsistent" behavior that's actually by design
3. **Balance Problems**: Can't balance characters with random ultimate assignments

## Recommended Fix Priority

### Priority 1 (Critical) - Immediate Fixes Required
1. **Implement Lightning Ultimate** - Fixes Lady Echo crashes
2. **Fix Random Ultimate Assignment** - Implement explicit character ultimate mapping

### Priority 2 (High) - Major Issues
3. **Fix Lady Fire and Ice** - Implement proper dual-element ultimate or choose one
4. **Update Documentation** - Correct ultimate system documentation

### Priority 3 (Medium) - Quality Issues
5. **Add Missing Gacha Rarity** - Complete character metadata
6. **Document Kboshi/Luna** - Update docs to reflect actual behavior

### Priority 4 (Low) - Cleanup
7. **Handle Orphaned Passives** - Remove or assign to characters

## Files Requiring Updates

### Code Fixes
- `backend/plugins/damage_types/lightning.py` - Add ultimate method
- `backend/plugins/damage_types/__init__.py` - Fix get_damage_type logic
- `backend/plugins/players/luna.py` - Add gacha_rarity
- `backend/plugins/players/lady_of_fire.py` - Add gacha_rarity

### Documentation Updates
- `.codex/docs/character-passives.md` - Correct ultimate information
- `.codex/implementation/character-types.md` - Update with actual ultimate assignments
- Character ability compilation document - Reflect reality vs documentation

## Testing Recommendations

### Immediate Testing Needed
1. **Lady Echo Ultimate Usage** - Verify crash reproduction
2. **Random Character Ultimates** - Document which ultimates each character can randomly receive
3. **Lady Fire and Ice Consistency** - Test multiple instantiations

### Regression Testing After Fixes
1. **All Character Ultimate Usage** - Verify proper ultimate assignment
2. **Save/Load Consistency** - Ensure ultimate assignments persist correctly
3. **Gacha System** - Verify rarity fixes don't break gacha mechanics

This completes the comprehensive discrepancy analysis between documented and actual character ability behavior.