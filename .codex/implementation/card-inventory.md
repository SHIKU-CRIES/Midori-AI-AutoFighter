# Card Inventory

`CardInventory.svelte` lists collected cards inside a shared `MenuPanel`. The
menu shows each card's name in a wrapped grid and displays a placeholder message
when no cards are owned. The inventory can be accessed during combat to review
collected cards and their effects.

## Testing
- `bun test`
## 1★ Cards
- Micro Blade – +3% ATK
- Polished Shield – +3% DEF
- Sturdy Vest – +3% HP
- Lucky Coin – +3% Crit Rate
- Sharpening Stone – +3% Crit Damage
- Mindful Tassel – +3% Effect Hit Rate
- Calm Beads – +3% Effect Res
- Energizing Tea – +3% Regain
- Thick Skin – +3% Bleed Resist
- Balanced Diet – +3% HP & +3% DEF
- Lightweight Boots – +3% Dodge Odds
- Expert Manual – +3% EXP Gain
- Steel Bangles – +3% Mitigation
- Enduring Charm – +3% Vitality
- Keen Goggles – +3% Crit Rate & +3% Effect Hit Rate
- Honed Point – +4% ATK
- Fortified Plating – +4% DEF
- Rejuvenating Tonic – +4% Regain
- Adamantine Band – +4% HP
- Precision Sights – +4% Crit Damage
- Inspiring Banner – +2% ATK & +2% DEF
- Tactical Kit – +2% ATK & +2% HP
- Bulwark Totem – +2% DEF & +2% HP
- Farsight Scope – +3% Crit Rate
- Steady Grip – +3% ATK & +3% Dodge Odds
- Coated Armor – +3% Mitigation & +3% DEF
- Guiding Compass – +3% EXP Gain & +3% Effect Hit Rate
- Swift Bandanna – +3% Crit Rate & +3% Dodge Odds
- Reinforced Cloak – +3% DEF & +3% Effect Res
- Vital Core – +3% Vitality & +3% HP
- Enduring Will – +3% Mitigation & +3% Vitality
- Battle Meditation – +3% EXP Gain & +3% Vitality
- Guardian Shard – +2% DEF & +2% Mitigation
- Sturdy Boots – +3% Dodge Odds & +3% DEF
- Spiked Shield – +3% ATK & +3% DEF
- 
## 2★ Cards
- Critical Focus – +55% ATK; start of turn grants Critical Boost stack
- Critical Transfer – Ultimates absorb Critical Boost stacks; +4% ATK per stack for that turn
- Iron Guard – +55% DEF; taking damage gives all allies +10% DEF for 1 turn
- Swift Footwork – +1 action per turn; first action each combat is free
- Mystic Aegis – +55% Effect Res; resisting a debuff heals 5% Max HP
- Vital Surge – +55% Max HP; while below 50% HP, +55% ATK
- Elemental Spark – +55% ATK & +55% Effect Hit Rate; one ally's debuffs gain +5% potency
- 
## 3★ Cards
- Critical Overdrive – +255% ATK; while an ally has Critical Boost, they gain +10% Crit Rate and convert excess Crit Rate to +2% Crit Damage.
- Iron Resurgence – +200% DEF & +200% HP; the first ally death revives at 10% HP and refreshes every 4 turns.
- Arc Lightning – +255% ATK; every attack chains 50% damage to a random foe.

## 4★ Cards
- Overclock – +240% ATK & +240% Effect Hit Rate; at the start of each battle, all allies immediately take two actions back to back.
- Iron Resolve – +240% DEF & +240% HP; the first time an ally dies, revive them at 30% HP. This effect refreshes every 3 turns.
- Arcane Repeater – +240% ATK; each attack has a 30% chance to immediately repeat at 50% power.
