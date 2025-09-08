# Update Character Documentation and Metadata

**Priority**: MEDIUM  
**Origin**: Character Ability Audit (17001dd5)  
**Impact**: Documentation accuracy and character metadata completeness  

## Problem Description

Multiple documentation and metadata issues were discovered during the character ability audit:

1. **Missing Gacha Rarity Fields**: Luna and Lady of Fire lack `gacha_rarity` fields
2. **Incorrect Ultimate Documentation**: Documentation claims characters have "custom damage types" when they actually use standard/random types
3. **Undocumented Ultimate Behavior**: Kboshi and Luna have working ultimates but documentation doesn't reflect their actual behavior

## Tasks

### Fix Missing Gacha Rarity Fields
- Coder, add `gacha_rarity = 5` to `backend/plugins/players/luna.py` (based on other 5★ characters)
- Coder, add `gacha_rarity = 5` to `backend/plugins/players/lady_of_fire.py` (assume 5★ unless specified otherwise)
- Coder, verify gacha system continues to function correctly with these additions

### Update Ultimate Documentation
- Coder, update `.codex/docs/character-passives.md` to reflect actual ultimate assignments:
  - Remove references to "custom damage types" for characters that use standard types
  - Document Kboshi's Dark ultimate usage
  - Document Luna's Generic ultimate usage
  - Update after random ultimate assignment fixes are completed

### Update Character Ability Compilation
- Coder, modify `.codex/audit/17001dd5-character-ability-compilation.audit.md` to reflect reality vs. documentation gaps
- Coder, create corrected character ability reference document for future use

### Address Orphaned Passives
- Task Master, decide whether to:
  - Remove unused passives (`advanced_combat_synergy`, `room_heal`)
  - Assign them to existing characters
  - Keep them for future character development
- Coder, implement Task Master's decision on orphaned passives

## Current Documentation Errors

### Gacha Rarity Missing
- **Luna**: No `gacha_rarity` field (should likely be 5★)
- **Lady of Fire**: No `gacha_rarity` field (should likely be 5★)

### Ultimate Documentation vs Reality
| Character | Documented | Actual Reality |
|-----------|------------|----------------|
| Kboshi | Custom Kboshi type | Dark ultimate |
| Luna | Custom Luna type | Generic ultimate |
| 8 others | Custom types | Random ultimates |

### Orphaned Implementations
- `advanced_combat_synergy.py` - Complete passive, no character uses it
- `room_heal.py` - Complete passive, no character uses it

## Acceptance Criteria

- [ ] All characters have proper `gacha_rarity` fields
- [ ] Documentation accurately reflects actual ultimate behavior
- [ ] No discrepancies between documented and actual character abilities
- [ ] Decision made on orphaned passive implementations
- [ ] Gacha system functions correctly with metadata updates

## Related Files

### Code Updates
- `backend/plugins/players/luna.py` - Add gacha_rarity
- `backend/plugins/players/lady_of_fire.py` - Add gacha_rarity

### Documentation Updates
- `.codex/docs/character-passives.md` - Correct ultimate information
- `.codex/audit/17001dd5-character-ability-compilation.audit.md` - Update compilation

### Potential Removals (after Task Master decision)
- `backend/plugins/passives/advanced_combat_synergy.py`
- `backend/plugins/passives/room_heal.py`

## Dependencies

This task should be completed after:
1. Lightning ultimate bug fix
2. Random ultimate assignment fix
3. Lady Fire and Ice ultimate fix

So that the documentation can accurately reflect the corrected ultimate system.

## Testing Requirements

- Verify gacha system displays and functions correctly with new rarity fields
- Confirm no runtime errors introduced by metadata changes
- Validate documentation accuracy against actual implementations

## Design Decisions Required

**Task Master, please decide on orphaned passives:**
- Should `advanced_combat_synergy` and `room_heal` be removed, assigned to characters, or kept for future use?
- If assigning to characters, which characters would benefit from these passive types?