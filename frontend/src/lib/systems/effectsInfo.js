// Canonical effect descriptions used across the UI
export const EFFECT_DESCRIPTIONS = {
  aftertaste: 'Deals a hit with random damage type (10% to 150% damage)',
  critical_boost: '+0.5% crit rate and +5% crit damage per stack. Removed when taking damage.',
  critboost: '+0.5% crit rate and +5% crit damage per stack. Removed when taking damage.',
  iron_guard: '+55% DEF; damage grants all allies +10% DEF for 1 turn.',
  elemental_spark: 'One random ally gains +5% effect hit rate until they take damage.',
  critical_focus: 'Low HP allies gain +25% critical hit rate.',
  arc_lightning: 'Lightning attacks may chain to a random foe for 50% damage.'
};

// Known shop items (cards/relics) that primarily showcase a specific effect.
// Map item id -> effect id to display that effect’s description in tooltips.
export const ITEM_EFFECT_MAP = {
  pocket_manual: 'aftertaste',
  critical_focus: 'critical_boost',
  elemental_spark: 'elemental_spark'
};

