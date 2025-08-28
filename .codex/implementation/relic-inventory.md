# Relic Inventory

`RelicInventory.svelte` uses `MenuPanel` to show a grid of relic names. If no
relics are held, the menu reports an empty inventory.

Relic entries display their stack count and expose their description as tooltip
text via the `about` field returned by the backend.

## Implemented Relics
- 1★ Rusty Buckle – Bleeds the weakest ally for 1% Max HP per stack and fires increasing Aftertaste bursts as they lose HP.
- 1★ Threadbare Cloak – Allies start battle with a shield equal to 3% Max HP per stack.
- 1★ Lucky Button – +3% Crit Rate; missed crits add +3% Crit Rate next turn.
 - 1★ Bent Dagger – +3% ATK; when a foe dies, allies gain +1% ATK for the rest of combat.
- 1★ Old Coin – +3% gold earned; first shop purchase refunded 3% of cost.
 - 1★ Shiny Pebble – +3% DEF per stack; the first time an ally is hit they gain +3% mitigation per stack for 1 turn.
 - 1★ Herbal Charm – Heals party members for 0.5% Max HP at the start of each turn.
 - 1★ Tattered Flag – +3% party Max HP; when an ally falls, survivors gain +3% ATK.
- 1★ Wooden Idol – +3% Effect Res; resisting a debuff grants +1% Effect Res next turn.
- 1★ Pocket Manual – +3% ATK; every 10th hit deals an extra 3% damage.
- 2★ Vengeful Pendant – Reflects 15% of damage taken back to the attacker.
- 2★ Arcane Flask – After an Ultimate, grant a shield equal to 20% Max HP per stack.
- 2★ Echo Bell – First action each battle repeats at 15% power per stack.
- 2★ Frost Sigil – Hits apply chill dealing 5% ATK as Aftertaste per stack.
- 2★ Ember Stone – Below 25% HP, allies burn their attacker for 50% ATK.
- 2★ Guardian Charm – Lowest-HP ally gains +20% DEF at battle start.
- 2★ Killer Instinct – Ultimates grant +75% ATK for the turn; kills grant another turn.
- 3★ Greed Engine – Party loses 1% HP per turn, gains +50% gold, and raises rare drop rate by 0.5% plus 0.1% per extra stack.
- 3★ Stellar Compass – Critical hits grant permanent +1.5% ATK and gold rate.
- 3★ Echoing Drum – First attack each battle repeats at 25% power.
- 4★ Null Lantern – Removes shops/rests; fights drop additional pulls.
- 4★ Traveler's Charm – When hit, gain +25% DEF and +10% mitigation next turn per stack.
- 4★ Timekeeper's Hourglass – Each turn, 10% +1% per stack chance for extra turns.
- 5★ Paradox Hourglass – 60% chance to sacrifice up to one ally per stack (max 4); survivors gain huge stat multipliers and foes lose defense.
- 5★ Soul Prism – Revives fallen allies at 1% HP with penalties (placeholder).
- 5★ Omega Core – Multiplies all stats by 6x plus 1x per stack for 10 turns +2 per stack before draining escalating HP.

## Testing
- `bun test`
