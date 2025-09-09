# Character Ability Audit - Documented Abilities Compilation

**Audit ID**: `17001dd5-character-ability-compilation`  
**Persona**: Coder  
**Date**: Generated during character ability audit task  
**Scope**: Complete compilation of all playable characters with their documented ultimates and passives

## Executive Summary

This document provides a comprehensive listing of all playable characters in the Midori AI AutoFighter game, cataloging their documented ultimates (via damage types) and passive abilities. The game features **18 playable characters** with varying implementations of ultimates and passives.

## Character Roster with Abilities

### Characters with Both Ultimates and Passives

#### 1. **Ally**
- **ID**: `ally`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Ally damage type
- **Ultimate**: Via Ally damage type (needs verification - custom type)
- **Passive**: `ally_overload` - Twin daggers scaling to Overload mode
- **Special**: Uses "pips" actions display

#### 2. **Bubbles**
- **ID**: `bubbles`
- **Character Type**: A (Masculine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Bubbles damage type
- **Ultimate**: Via Bubbles damage type (needs verification - custom type)
- **Passive**: `bubbles_bubble_burst` - Element switching with bubble stacking
- **Special**: Uses "pips" actions display

#### 3. **Carly**
- **ID**: `carly`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Light
- **Ultimate**: Light Ultimate - Full party heal + enemy defense debuff
- **Passive**: `carly_guardians_aegis` - Defense-focused abilities
- **Special**: ATK→Defense stat conversion, uses "number" actions display

#### 4. **Graygray**
- **ID**: `graygray`
- **Character Type**: A (Masculine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Graygray damage type
- **Ultimate**: Via Graygray damage type (needs verification - custom type)
- **Passive**: `graygray_counter_maestro` - Counter-attacks with stacking buffs
- **Special**: Uses "pips" actions display

#### 5. **Hilander**
- **ID**: `hilander`
- **Character Type**: A (Masculine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Hilander damage type
- **Ultimate**: Via Hilander damage type (needs verification - custom type)
- **Passive**: `hilander_critical_ferment` - Crit stacking mechanics
- **Special**: Uses "pips" actions display

#### 6. **Kboshi**
- **ID**: `kboshi`
- **Character Type**: A (Masculine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Kboshi damage type
- **Ultimate**: Via Kboshi damage type (needs verification - custom type)
- **Passive**: `kboshi_flux_cycle` - Element switching with damage/HoT stacking
- **Special**: Uses "pips" actions display

#### 7. **Lady Darkness**
- **ID**: `lady_darkness`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Dark
- **Ultimate**: Dark Ultimate - Multi-hit scaling with DoT stacks
- **Passive**: `lady_darkness_eclipsing_veil` - Shadow-based mechanics
- **Special**: Uses "pips" actions display

#### 8. **Lady Echo**
- **ID**: `lady_echo`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Lightning
- **Ultimate**: **MISSING** - Lightning damage type has NO ultimate implementation
- **Passive**: `lady_echo_resonant_static` - Lightning/echo effects
- **Special**: Uses "pips" actions display

#### 9. **Lady Light**
- **ID**: `lady_light`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Light
- **Ultimate**: Light Ultimate - Full party heal + enemy defense debuff (shared with Carly)
- **Passive**: `lady_light_radiant_aegis` - Light-based protection
- **Special**: Uses "pips" actions display

#### 10. **Lady of Fire**
- **ID**: `lady_of_fire`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: **MISSING** (no gacha_rarity field)
- **Damage Type**: Fire
- **Ultimate**: Fire Ultimate - AoE damage with DoT application
- **Passive**: `lady_of_fire_infernal_momentum` - Fire-based mechanics
- **Special**: Uses "pips" actions display

#### 11. **Luna**
- **ID**: `luna`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: **MISSING** (no gacha_rarity field)
- **Damage Type**: Custom Luna damage type
- **Ultimate**: Via Luna damage type (needs verification - custom type)
- **Passive**: `luna_lunar_reservoir` - Charge-based attack scaling
- **Special**: Uses "number" actions display

#### 12. **Mezzy**
- **ID**: `mezzy`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Mezzy damage type
- **Ultimate**: Via Mezzy damage type (needs verification - custom type)
- **Passive**: `mezzy_gluttonous_bulwark` - Damage reduction + stat siphoning
- **Special**: Uses "pips" actions display

#### 13. **Player**
- **ID**: `player`
- **Character Type**: C (Androgynous)
- **Gacha Rarity**: **MISSING** (no gacha_rarity field)
- **Damage Type**: Fire (default, customizable)
- **Ultimate**: Fire Ultimate - AoE damage with DoT application (default)
- **Passive**: `player_level_up_bonus` - Enhanced stat gains on level up
- **Special**: Customizable damage type, pronouns, and stats

### Characters with Passives but Missing/Unclear Ultimates

#### 14. **Becca**
- **ID**: `becca`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Becca damage type
- **Ultimate**: Via Becca damage type (needs verification - custom type)
- **Passive**: `becca_menagerie_bond` - Variable mechanics
- **Special**: Uses "pips" actions display

#### 15. **Ixia**
- **ID**: `ixia`
- **Character Type**: A (Masculine)
- **Gacha Rarity**: 5★
- **Damage Type**: Lightning
- **Ultimate**: Lightning ultimate (needs verification)
- **Passive**: `ixia_tiny_titan` - Size-based mechanics
- **Special**: Uses "pips" actions display

#### 16. **Lady Fire and Ice**
- **ID**: `lady_fire_and_ice`
- **Character Type**: B (Feminine)
- **Gacha Rarity**: 6★
- **Damage Type**: Custom LadyFireAndIce damage type
- **Ultimate**: Via LadyFireAndIce damage type (needs verification - custom type)
- **Passive**: `lady_fire_and_ice_duality_engine` - Dual-element mechanics
- **Special**: Uses "pips" actions display

#### 17. **Mimic**
- **ID**: `mimic`
- **Character Type**: C (Androgynous)
- **Gacha Rarity**: 5★
- **Damage Type**: Custom Mimic damage type
- **Ultimate**: Via Mimic damage type (needs verification - custom type)
- **Passive**: `mimic_player_copy` - Copying/adaptive mechanics
- **Special**: Uses "pips" actions display

## Ultimate System Analysis

### Implemented Ultimate Types

1. **Light Ultimate** (`light.py`)
   - Full party heal to max HP
   - Removes all DoTs including Shadow Siphon
   - Applies defense debuff to enemies for 10 turns
   - Used by: Carly, Lady Light

2. **Fire Ultimate** (`fire.py`)
   - AoE damage to all living enemies
   - Applies DoT effects where possible
   - Increases drain stacks for future damage scaling
   - Used by: Lady of Fire, Player (default)

3. **Dark Ultimate** (`dark.py`)
   - Six-hit combo scaling with allied DoT stacks
   - High scaling potential with DoT synergy
   - Used by: Lady Darkness

4. **Ice Ultimate** (`ice.py`)
   - Six strikes to all foes with ramping damage
   - 30% damage increase per target
   - Used by: **No character currently uses Ice damage type**

5. **Wind Ultimate** (`wind.py`)
   - Complex DoT transfer and damage mechanics
   - Multi-phase attack with temporary buffs
   - Used by: **No character currently uses Wind damage type**

6. **Generic Ultimate** (`generic.py`)
   - Fallback ultimate for custom damage types
   - Triggers passives on random targets
   - Used by: All characters with custom damage types

### Missing Ultimate Types

1. **Lightning Ultimate** - **COMPLETELY MISSING**
   - Lightning damage type (`lightning.py`) has NO ultimate method
   - Affects: Lady Echo (uses Lightning damage type)

## Passive System Analysis

### Implemented Passives (21 total)

1. `ally_overload` - Twin dagger mechanics
2. `attack_up` - Basic attack enhancement  
3. `becca_menagerie_bond` - Variable/adaptive mechanics
4. `bubbles_bubble_burst` - Element switching with bubbles
5. `carly_guardians_aegis` - Defense-focused protection
6. `ixia_tiny_titan` - Size-based mechanics
7. `graygray_counter_maestro` - Counter-attack stacking
8. `hilander_critical_ferment` - Critical hit mechanics
9. `kboshi_flux_cycle` - Element cycling mechanics
10. `lady_darkness_eclipsing_veil` - Shadow abilities
11. `lady_echo_resonant_static` - Lightning/echo effects
12. `lady_fire_and_ice_duality_engine` - Dual-element mechanics
13. `lady_light_radiant_aegis` - Light-based protection
14. `lady_of_fire_infernal_momentum` - Fire progression mechanics
15. `luna_lunar_reservoir` - Charge-based attack scaling
16. `mezzy_gluttonous_bulwark` - Damage reduction + siphoning
17. `mimic_player_copy` - Copying/adaptive mechanics
18. `player_level_up_bonus` - Enhanced stat gains
19. `advanced_combat_synergy` - **Unused** - No character references this
20. `room_heal` - **Unused** - No character references this

## Critical Issues Identified

### 1. Missing Ultimate Implementation
- **Lightning damage type has NO ultimate method**
- Affects Lady Echo (Lightning damage type user)
- This is a functional gap that breaks ultimate usage for Lightning characters

### 2. Missing Gacha Rarity
- Luna (no gacha_rarity field)
- Lady of Fire (no gacha_rarity field)  
- Player (no gacha_rarity field - expected as Player is special)

### 3. Orphaned Passives
- `advanced_combat_synergy` - Implemented but no character uses it
- `room_heal` - Implemented but no character uses it

### 4. Custom Damage Type Coverage
- 11 characters use custom damage types that need verification
- All rely on Generic Ultimate fallback which may not provide intended mechanics

### 5. Shared Ultimate Types
- Light Ultimate shared between Carly and Lady Light (may be intentional)
- Fire Ultimate used by Lady of Fire and Player default (may be intentional)

## Verification Needed

### Custom Damage Types to Inspect
1. Ally damage type implementation
2. Becca damage type implementation  
3. Bubbles damage type implementation
4. Ixia damage type implementation
5. Graygray damage type implementation
6. Hilander damage type implementation
7. Kboshi damage type implementation
8. Lady Fire and Ice damage type implementation
9. Luna damage type implementation
10. Mezzy damage type implementation
11. Mimic damage type implementation

### Passive Functionality to Verify
- All 18 character-specific passives need behavior verification
- Cross-reference with existing documentation in `.codex/docs/character-passives.md`

## Next Steps

1. **Immediate**: Inspect actual implementation files for custom damage types
2. **Immediate**: Verify passive implementations match documented behavior
3. **Critical**: Address Lightning Ultimate missing implementation
4. **Important**: Resolve missing gacha_rarity fields
5. **Cleanup**: Determine fate of orphaned passives

## Documentation References

- Primary passive documentation: `.codex/docs/character-passives.md`
- Character type documentation: `.codex/implementation/character-types.md`
- Implementation files: `backend/plugins/players/`, `backend/plugins/passives/`, `backend/plugins/damage_types/`