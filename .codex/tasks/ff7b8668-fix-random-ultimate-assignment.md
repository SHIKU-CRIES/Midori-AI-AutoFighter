# Support Gacha Damage Type Persistence System

**Priority**: HIGH  
**Origin**: Character Ability Audit (17001dd5) + User Clarification  
**Impact**: Major gameplay design enhancement for gacha mechanics  

## Problem Description

The current random damage type assignment system is intentionally designed for gacha mechanics where players can pull different elemental variants of characters (e.g., "fire type mezzy", "ice type mezzy"). However, the implementation may need refinement to ensure:

1. **Persistence**: Characters maintain consistent damage types within game sessions
2. **Display**: Players can see what damage type their character instance has
3. **Balance**: Gacha damage type assignment works as intended

**Current System**: Characters like Ally, Becca, Bubbles, Ixia, Graygray, Hilander, Mezzy, Mimic call `get_damage_type("CharacterName")` which falls back to `random_damage_type()` when no specific mapping exists.

## User Requirements (Clarified)

- ✅ **Random damage types are intentional** for gacha system
- ❓ **When is damage type determined?** (at gacha pull vs character instantiation)
- ❓ **Should damage type persist** between battle sessions?
- ❓ **How should damage type be displayed** to players?

## Design Questions to Resolve

### 1. Damage Type Assignment Timing
- **Option A**: Assign once during gacha pull and store persistently
- **Option B**: Assign during character creation in each game session  
- **Option C**: Assign during battle instantiation (current behavior)

### 2. Persistence Strategy
- **Option A**: Store damage type in character save data
- **Option B**: Consistent within game session only
- **Option C**: Pure random each instantiation (current)

### 3. Display and UI
- How should players know what damage type their character has?
- Should gacha results show the damage type pulled?
- Should character selection show damage type?

## Implementation Tasks (After Design Decision)

### If Option A (Persistent Gacha Assignment):
- Coder, modify gacha system to assign and store damage types during character pull
- Coder, update character instantiation to use stored damage type
- Coder, add damage type display in character selection UI
- Coder, add damage type information to gacha pull results

### If Option B (Session Consistent):
- Coder, modify character instantiation to use deterministic seeding per session
- Coder, ensure consistent assignment within battle chains
- Coder, add session-based damage type display

### If Option C (Current Random):
- Task Master, clarify if current implementation meets requirements
- Coder, add real-time damage type display for players
- Coder, document intended random behavior

## Current Affected Characters

| Character | Current Behavior | Gacha Rarity |
|-----------|------------------|--------------|
| Ally | Random per instantiation | 5 |
| Becca | Random per instantiation | 5 |
| Bubbles | Random per instantiation | 5 |
| Ixia | Lightning | 5 |
| Graygray | Random per instantiation | 5 |
| Hilander | Random per instantiation | 5 |
| Mezzy | Random per instantiation | 5 |
| Mimic | Random per instantiation | 5 |

## Acceptance Criteria

- [ ] Design decision made on damage type assignment timing
- [ ] Implementation aligns with intended gacha mechanics
- [ ] Players can understand what damage type their character has
- [ ] Damage type behavior is consistent with chosen design
- [ ] Documentation reflects intended behavior
- [ ] All tests pass with new implementation

## Related Files

- `backend/plugins/damage_types/__init__.py` - get_damage_type function
- `backend/autofighter/gacha.py` - Gacha system
- `backend/plugins/players/` - Affected character files
- Character selection and battle UI components
- `.codex/docs/character-passives.md` - Documentation updates

## Dependencies

This task should be completed after:
1. ✅ Lightning ultimate bug fix (completed)
2. User clarification on design decisions
3. Lady Fire and Ice behavior decision

## Testing Requirements

- Unit tests verifying chosen damage type behavior
- Integration tests with gacha system (if persistent)
- Manual testing of character selection and battle usage
- UI testing for damage type display