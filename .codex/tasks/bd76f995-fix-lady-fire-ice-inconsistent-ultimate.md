# Fix Lady Fire and Ice Inconsistent Ultimate

**Priority**: HIGH  
**Origin**: Character Ability Audit (17001dd5)  
**Impact**: Character behavior varies randomly between game sessions  

## Problem Description

Lady Fire and Ice randomly receives either Fire ultimate OR Ice ultimate due to substring matching in the `get_damage_type()` function. The character name contains both "fire" and "ice" substrings, causing `choice()` to randomly select between them.

**Current Behavior**:
- Sometimes gets Fire ultimate (AoE damage + DoT application)
- Sometimes gets Ice ultimate (6-hit ramping damage)
- Player cannot predict which ultimate the character will have

## Root Cause

```python
# In get_damage_type(), both substrings match:
matches = ["Fire", "Ice"]  # Both "fire" and "ice" found in "lady_fire_and_ice"
return _load_cls(choice(matches))()  # Random selection each instantiation
```

## Design Decision Required

**Task Master, choose one of these solutions:**

### Option A: Implement True Dual-Element Ultimate
- Create custom `LadyFireAndIce` damage type with unique dual-element ultimate
- Ultimate combines Fire and Ice effects (e.g., burning then freezing)
- Most thematically appropriate but requires new implementation

### Option B: Fix to Consistent Single Element
- Modify `get_damage_type()` to always return same element for Lady Fire and Ice
- Choose Fire OR Ice as permanent assignment
- Simple fix but loses dual-element theme

### Option C: Alternating Element System
- Implement element switching mechanic as part of character's ultimate
- Ultimate alternates between Fire and Ice effects predictably
- Preserves dual-element theme with predictable behavior

## Tasks

### After design decision:

#### Option A Tasks (Dual-Element Ultimate)
- Coder, create `backend/plugins/damage_types/lady_fire_and_ice.py` with custom damage type
- Coder, implement unique dual-element ultimate combining Fire and Ice effects
- Coder, modify `get_damage_type()` to return custom type for "lady_fire_and_ice"
- Coder, add comprehensive tests for dual-element ultimate

#### Option B Tasks (Single Element Fix)
- Coder, modify `get_damage_type()` substring matching to prioritize one element
- Coder, update documentation to reflect chosen element
- Coder, ensure consistent behavior across all game sessions

#### Option C Tasks (Alternating Elements)
- Coder, implement state tracking for element alternation
- Coder, modify ultimate behavior to switch between Fire and Ice predictably
- Coder, add UI indicators for current element state

### Common Tasks
- Coder, add unit tests verifying consistent behavior
- Coder, update character documentation with chosen ultimate behavior
- Coder, verify character works correctly in battle scenarios

## Current Character Details

- **ID**: `lady_fire_and_ice`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 6★
- **Passive**: `lady_fire_and_ice_duality_engine` (dual-element mechanics)

## Acceptance Criteria

- [ ] Lady Fire and Ice has predictable ultimate behavior
- [ ] Ultimate assignment is consistent across all game sessions
- [ ] Chosen solution aligns with character's dual-element theme
- [ ] All existing functionality remains intact
- [ ] Documentation reflects actual behavior

## Related Files

- `backend/plugins/damage_types/__init__.py` - get_damage_type function
- `backend/plugins/players/lady_fire_and_ice.py` - Character definition
- `backend/plugins/passives/lady_fire_and_ice_duality_engine.py` - Related passive
- Potentially new: `backend/plugins/damage_types/lady_fire_and_ice.py`

## Testing Requirements

- Multiple instantiations must yield identical ultimate behavior
- Ultimate effects must be thematically consistent with character design
- Battle integration testing to verify ultimate functionality
- Save/load testing to ensure ultimate assignment persists

## Priority Justification

While not game-breaking like the Lightning bug, this creates a poor player experience where character behavior is unpredictable. The 6★ rarity suggests this is a premium character that should have reliable, consistent mechanics.