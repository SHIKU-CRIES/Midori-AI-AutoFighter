# Character Passives and Ultimates Audit

This task list catalogs each playable character's listed passive ability and ultimate element and notes how the implementation behaves in code. Use these notes to reconcile documentation with actual mechanics.

## Ally
- **Passive – Overload**: Claimed to build charge from twin daggers and enter an Overload stance at 100 charge.
  - **Actual**: `AllyOverload` grants two attacks per turn, builds 10 charge per action with reduced gains past 120, and Overload quadruples attacks while applying damage bonuses and vulnerabilities. Effects rely on manual `_active_effects` management and lack full effect-system integration.
- **Ultimate – Random element**: Damage type chosen randomly; ultimate depends on rolled element.
- **Tasks**:
  - Integrate Overload effect removal with the `EffectManager` instead of directly editing `_active_effects`.
  - Confirm random element persists across sessions or select a fixed element.

## Becca
- **Passive – Menagerie Bond**: Claimed to summon jellyfish and grant spirit-based bonuses.
  - **Actual**: `BeccaMenagerieBond` summons one of four jellyfish at the cost of HP, tracks spirit stacks, and buffs both Becca and summons, but cooldown and buff synchronization are complex.
- **Ultimate – Random element**
- **Tasks**:
  - Simplify summon management and ensure cooldown/HP costs are enforced.
  - Verify spirit bonuses remove correctly when summons disappear.

## Bubbles
- **Passive – Bubble Burst**: Alternates elements and bursts after three hits per foe.
  - **Actual**: `BubblesBubbleBurst` rotates damage type each action and tracks hits per foe; burst applies damage and removes stacks.
- **Ultimate – Random element**
- **Tasks**:
  - Check that element rotation aligns with combat log and that burst resets per-foe counters.

## Carly
- **Passive – Guardian's Aegis**: Supposed to heal allies and convert attack growth into defense.
  - **Actual**: `CarlyGuardiansAegis` heals lowest ally, converts attack stat gains to defense, builds mitigation stacks that can overcharge, and shares mitigation on ultimate.
- **Ultimate – Light**: `Light` ultimate heals allies to full, removes DoTs, and applies defense down to foes.
- **Tasks**:
  - Verify mitigation stack decay and overcharge conversions.
  - Ensure ultimate cleans up Shadow Siphon and other DoTs as intended.

## Chibi
- **Passive – Tiny Titan**: Gains four times Vitality benefits.
  - **Actual**: `ChibiTinyTitan` multiplies stat bonuses from Vitality by four.
- **Ultimate – Random element**
- **Tasks**:
  - Confirm Vitality multipliers apply after buffs and scale with level appropriately.

## Graygray
- **Passive – Counter Maestro**: Counterattacks on hit and bursts at 50 stacks.
  - **Actual**: `GraygrayCounterMaestro` tracks counter stacks, counterattacks when damaged, and releases max-HP burst at 50 stacks.
- **Ultimate – Random element**
- **Tasks**:
  - Ensure counters reset properly after burst and that burst damage scales with max HP.

## Hilander
- **Passive – Critical Ferment**: Builds crit rate/damage stacks and consumes one on crit.
  - **Actual**: `HilanderCriticalFerment` adds +5% crit rate and +10% crit damage per hit, drops stack gain odds past 20, and on crit triggers Aftertaste then removes highest stack.
- **Ultimate – Random element**
- **Tasks**:
  - Confirm stack removal works for both crit rate and damage effects.
  - Decide on a fixed element if random damage type is not desired.

## Kboshi
- **Passive – Flux Cycle**: Randomly changes damage type, failed switches grant stacking bonuses.
  - **Actual**: `KboshiFluxCycle` attempts to switch element each action; failed rolls build Flux stacks that boost stats and are consumed on successful switch, applying mitigation debuff to foes.
- **Ultimate – Random element**
- **Tasks**:
  - Review probability curve for element switching and ensure debuffs apply to all foes.

## Lady Darkness
- **Passive – Eclipsing Veil**: Baseline dark-themed fighter.
  - **Actual**: `LadyDarknessEclipsingVeil` applies themed stat buffs; minimal unique behavior.
- **Ultimate – Dark**: `Dark` ultimate strikes six times and scales with allied DoT stacks.
- **Tasks**:
  - Flesh out passive effects or document intentionally minimal design.

## Lady Echo
- **Passive – Resonant Static**: Baseline lightning-themed fighter.
  - **Actual**: `LadyEchoResonantStatic` focuses on electrical flavor with modest effects.
- **Ultimate – Lightning**: Deals attack damage, applies random DoTs, and builds Aftertaste stacks that trigger on subsequent hits.
- **Tasks**:
  - Clarify passive benefits and ensure Aftertaste stacks clear at battle end.

## Lady Fire and Ice
- **Passive – Duality Engine**: Alternates between Fire and Ice to build Flux and penalize repeated elements.
  - **Actual**: `LadyFireAndIceDualityEngine` swaps elements each action, tracks Flux stacks, and reduces foe mitigation when repeating an element.
- **Ultimate – Fire or Ice**: Damage type chosen at load; Fire ult AOE DoT, Ice ult six ramping hits.
- **Tasks**:
  - Guarantee element alternation persists after battle and Flux resets correctly.

## Lady Light
- **Passive – Radiant Aegis**: Baseline light-themed fighter.
  - **Actual**: `LadyLightRadiantAegis` grants defensive light-themed buffs.
- **Ultimate – Light**
- **Tasks**:
  - Expand passive description or effects to differentiate from Carly.

## Lady of Fire
- **Passive – Infernal Momentum**: Baseline fire-themed fighter.
  - **Actual**: `LadyOfFireInfernalMomentum` offers minimal fire-aligned bonuses.
- **Ultimate – Fire**
- **Tasks**:
  - Determine if additional fire mechanics are needed beyond base damage type.

## Luna
- **Passive – Lunar Reservoir**: Builds actions and stores charges for burst turns.
  - **Actual**: `LunaLunarReservoir` manages action counters, granting extra actions after enough turns.
- **Ultimate – Generic**: Generic ultimate performs 64 tiny hits on one target.
- **Tasks**:
  - Audit action counter reset logic and ensure generic ultimate fits character theme.

## Mezzy
- **Passive – Gluttonous Bulwark**: Raises max HP, reduces damage taken, siphons stats from healthy allies.
  - **Actual**: `MezzyGluttonousBulwark` steals fractions of allies' stats each turn while building defenses.
- **Ultimate – Random element**
- **Tasks**:
  - Confirm stat siphon reverses when allies fall and doesn't permanently drain party.

## Mimic
- **Passive – Player Copy**: Copies player stats then reduces them.
  - **Actual**: `MimicPlayerCopy` clones the player's build and applies a 25% stat penalty.
- **Ultimate – Random element**
- **Tasks**:
  - Check cloning process for edge cases and ensure penalty applies uniformly.

## Player (Generic Avatar)
- **Passive – Level Up Bonus**: Grants bonuses on player level-ups.
  - **Actual**: `PlayerLevelUpBonus` awards small stat increases each level.
- **Ultimate – Chosen damage type**
- **Tasks**:
  - Confirm level-up bonuses scale with player progression and respect damage-type-specific ultimates.

---

Developers should review each section, verify behavior against design goals, and implement fixes or clarifications as needed.
