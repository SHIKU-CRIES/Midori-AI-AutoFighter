# Battle Review Icon Layout

The Battle Review interface uses a vertical icon column and a persistent side panel:

- Navigation icons appear in a left-side column. The overview uses a Swords icon, while party and foe entries show their portraits.
- Selecting an icon swaps the main content without hiding statistics; the right-side stats panel updates for the active entry.
- `.battle-review-tabs` arranges three columns: `icon-column`, `content-area`, and `stats-panel`.
- `.icon-btn` provides a square click target with hover and active states.
- The stats panel hosts the `entity-stats-grid`, ensuring key metrics stay visible during navigation.
- Colors should match the UI's stained-glass palette, using vibrant hues such
  as those returned by `getElementBarColor` in `frontend/src/lib/BattleReview.svelte`.
