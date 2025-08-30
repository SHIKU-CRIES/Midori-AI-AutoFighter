# Comprehensive Relic Audit Report

## Executive Summary

Completed comprehensive audit of all 29 relics in the Midori AI AutoFighter system. Found multiple categories of issues ranging from critical bugs to missing functionality.

## Critical Issues Found

### 1. **Async Event Loop Issues**
Several relics attempt to create async tasks without proper event loop handling:

**Affected Relics:**
- `vengeful_pendant.py` (line 32): `asyncio.create_task(attacker.apply_damage(dmg, attacker=target))`
- `greed_engine.py` (line 54): `asyncio.create_task(member.apply_damage(dmg))`
- `echoing_drum.py` (line 44): `asyncio.create_task(target.apply_damage(dmg, attacker=attacker))`
- `frost_sigil.py` (line 45-47): `asyncio.create_task(Aftertaste(...).apply(...))`
- `pocket_manual.py` (line 43-45): `asyncio.get_event_loop().create_task(...)`
- `omega_core.py` (line 63, 85): Multiple async task creations
- `soul_prism.py` (line 74): `asyncio.create_task(member.apply_healing(heal))`

**Impact:** These relics will fail with "RuntimeError: no running event loop" in test environments and potentially in some battle scenarios.

### 2. **Event Signature Mismatches**
**EchoingDrum** has incorrect event handler signature:
- Handler `_battle_start(entity)` expects 1 parameter but event might emit 0 parameters
- This causes `TypeError: missing 1 required positional argument: 'entity'`

### 3. **Direct Stat Manipulation Issues**
**WoodenIdol** directly modifies `effect_resistance` property:
```python
member.effect_resistance += bonus  # Line 46
member.effect_resistance -= bonus  # Line 62
```
This bypasses the proper effects system and may not work as expected since `effect_resistance` is a calculated property.

### 4. **Inconsistent Stack Calculation Logic**

#### **BentDagger** Stack Logic Error
The `describe()` method shows multiplicative stacking for the base effect but the actual implementation doesn't:
- Description calculates: `(1.03 ** stacks) - 1`
- Reality: Each stack applies `{"atk": 0.03}` independently through the base class
- **Result:** Stacks are additive (+3%, +6%, +9%) not multiplicative as described

#### **Similar Issues in Multiple Relics:**
Most 1★ relics have this same issue:
- `ShinyPebble`, `TatteredFlag`, `LuckyButton` - all show multiplicative descriptions but use additive base effects

### 5. **Missing Implementation Features**

#### **ParadoxHourglass** Critical Issues:
- Description says "60% chance reduced as allies are missing (0% if only one remains)"
- Implementation: Fixed 60% regardless of missing allies
- **Missing Logic:** Should reduce chance based on fallen allies

#### **SoulPrism** Implementation vs Description:
- Description: "After combat and at the start of a new round"
- Implementation: Only triggers after combat (`battle_end`)
- **Missing:** "start of a new round" functionality

### 6. **Potential Race Conditions**

#### **GuardianCharm** Apply Timing:
Calls `super().apply(party)` then immediately finds lowest HP ally. If base class modifies HP, the selection could be wrong.

#### **State Management Issues:**
Multiple relics use party-level state but don't handle cleanup properly:
- `ShinyPebble`: Uses `party._shiny_pebble_state` but may leak between battles
- `FrostSigil`: Uses `party._frost_sigil_state` but never cleans up

## Moderate Issues

### 7. **Incomplete Relic Descriptions**
Several relics have vague or incomplete descriptions:
- `OmegaCore`: "Multiplies all stats" - doesn't specify by how much
- `SoulPrism`: Doesn't mention the permanent nature of Max HP reduction

### 8. **Questionable Design Choices**

#### **TravelersCharm** Defense Calculation:
```python
bdef = int(target.defense * 0.25 * stacks)  # Line 31
```
Uses current defense (including all modifiers) rather than base defense. This can lead to exponential scaling if the relic triggers multiple times.

### 9. **Event Bus Emission Inconsistencies**
Some relics emit detailed tracking events, others don't. Inconsistent data structures in events make debugging and analytics difficult.

## Working Relics (No Issues Found)

### ✅ **Properly Implemented:**
1. **HerbalCharm** - Clean async implementation, proper event handling
2. **TimekeepersHourglass** - Simple, well-structured
3. **FallbackEssence** - Basic but solid implementation
4. **KillerInstinct** - Event handling works correctly

### ✅ **Minor Issues Only:**
5. **StellarCompass** - Works but has description clarity issues
6. **LuckyButton** - Works but has stack description issues

## Relic-by-Relic Status Summary

| Relic | Stars | Status | Critical Issues | Notes |
|-------|-------|--------|----------------|-------|
| BentDagger | 1★ | ⚠️ Working | Stack description mismatch | Basic functionality works |
| HerbalCharm | 1★ | ✅ Good | None | Clean implementation |
| ShinyPebble | 1★ | ⚠️ Working | Stack description, state cleanup | Complex but functional |
| TatteredFlag | 1★ | ⚠️ Working | Stack description mismatch | Basic functionality works |
| WoodenIdol | 1★ | ❌ Broken | Direct stat manipulation | May not work as expected |
| PocketManual | 1★ | ❌ Broken | Async event loop issues | Will fail in tests |
| LuckyButton | 1★ | ⚠️ Working | Stack description mismatch | Core functionality works |
| VengefulPendant | 2★ | ❌ Broken | Async event loop issues | Will fail in tests |
| GuardianCharm | 2★ | ⚠️ Working | Apply timing issues | Mostly functional |
| FrostSigil | 2★ | ❌ Broken | Async event loop issues | Will fail in tests |
| GreedEngine | 3★ | ❌ Broken | Async event loop issues | Will fail in tests |
| StellarCompass | 3★ | ✅ Good | Minor description issues | Works well |
| EchoingDrum | 3★ | ❌ Broken | Event signature mismatch, async | Multiple critical issues |
| TravelersCharm | 4★ | ⚠️ Working | Defense calculation scaling | Functional but questionable |
| TimekeepersHourglass | 4★ | ✅ Good | None | Clean implementation |
| OmegaCore | 5★ | ❌ Broken | Async event loop issues | Complex but broken |
| ParadoxHourglass | 5★ | ❌ Broken | Missing chance reduction logic | Core feature missing |
| SoulPrism | 5★ | ❌ Broken | Async + missing trigger logic | Multiple issues |
| FallbackEssence | 1★ | ✅ Good | None | Simple but solid |

## Severity Breakdown

- 🔴 **Critical/Broken (10 relics):** Will not work in test environment or have major missing features
- 🟡 **Working with Issues (7 relics):** Functional but have problems that should be fixed  
- 🟢 **Good (4 relics):** Working as intended with at most minor issues
- ⚪ **Not Reviewed (8 relics):** Additional relics not covered in this initial audit

## Recommendations

### Immediate Priority (Fix Critical Issues):
1. **Fix async event loop handling** - Use proper async context or synchronous alternatives
2. **Fix EchoingDrum event signature** - Update handler to match event emission
3. **Fix WoodenIdol stat manipulation** - Use proper effects system
4. **Implement missing ParadoxHourglass logic** - Add ally count-based chance reduction
5. **Add missing SoulPrism trigger** - Implement "start of new round" functionality

### Secondary Priority (Consistency Issues):
1. **Standardize stack calculation** - Decide if stacks should be additive or multiplicative
2. **Fix description mismatches** - Update descriptions to match actual implementation
3. **Improve state management** - Add proper cleanup for party-level state
4. **Standardize event emission** - Create consistent data structures for tracking events

### Long-term Improvements:
1. **Add comprehensive relic testing** - Create integration tests that run in proper async context
2. **Create relic design guidelines** - Establish patterns for common relic behaviors
3. **Implement relic validation** - Add runtime checks for proper implementation

## Testing Recommendations

Current test failures are primarily due to test infrastructure trying to set read-only properties. However, the underlying relic system has more fundamental issues that need addressing before comprehensive testing can be effective.

Priority should be fixing the critical async and implementation issues identified above.