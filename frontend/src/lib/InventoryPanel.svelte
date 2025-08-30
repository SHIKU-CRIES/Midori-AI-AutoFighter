<script>
  import CurioChoice from './CurioChoice.svelte';
  import CardArt from './CardArt.svelte';
  import { onMount } from 'svelte';
  import { getCardCatalog, getRelicCatalog } from './api.js';
  export let cards = [];
  export let relics = [];
  const count = (arr) => {
    const map = {};
    for (const id of arr) {
      map[id] = (map[id] || 0) + 1;
    }
    return Object.entries(map);
  };

  // Catalog metadata maps for richer display
  let cardMeta = {};
  let relicMeta = {};

  onMount(async () => {
    try {
      const [cards, relics] = await Promise.all([getCardCatalog(), getRelicCatalog()]);
      cardMeta = Object.fromEntries(cards.map(c => [c.id, c]));
      relicMeta = Object.fromEntries(relics.map(r => [r.id, r]));
    } catch (e) {
      // Silently ignore; components will fallback to id-only display
    }
  });

  // Helpers to resolve stars and names safely
  const cardStars = (id) => (cardMeta?.[id]?.stars ?? 1) | 0;
  const relicStars = (id) => (relicMeta?.[id]?.stars ?? 1) | 0;
  const cardName = (id) => String(cardMeta?.[id]?.name || id);
  const relicName = (id) => String(relicMeta?.[id]?.name || id);

  // Sort order: Cards section first (already rendered first), then Relics.
  // Within each section: sort by star rank descending, then by name A→Z for stability.
  $: cardIdsUnique = Array.from(new Set(cards || []));
  $: sortedCardIds = [...cardIdsUnique].sort((a, b) => {
    const s = cardStars(b) - cardStars(a);
    if (s !== 0) return s;
    return cardName(a).localeCompare(cardName(b));
  });

  $: relicEntries = count(relics || []); // [id, qty]
  $: sortedRelicEntries = [...relicEntries].sort((a, b) => {
    const [idA] = a; const [idB] = b;
    const s = relicStars(idB) - relicStars(idA);
    if (s !== 0) return s;
    return relicName(idA).localeCompare(relicName(idB));
  });
</script>

<div class="inv-root" data-testid="inventory-panel">
  {#if cards.length}
    <h3>Cards</h3>
    <div class="cards-grid">
      {#each sortedCardIds as id}
        {#key id}
          <div class="item">
            <CardArt entry={{ id, name: cardName(id), stars: cardStars(id), about: (cardMeta[id]?.about || '') }} type="card" />
          </div>
        {/key}
      {/each}
    </div>
  {/if}
  {#if relics.length}
    <h3>Relics</h3>
    <div class="relics-grid">
      {#each sortedRelicEntries as [id, qty]}
        {#key id}
          <div class="item">
            <CurioChoice entry={{ id, name: relicName(id), stars: relicStars(id), about: (relicMeta[id]?.about || '') }} />
            <span class="qty">x{qty}</span>
          </div>
        {/key}
      {/each}
    </div>
  {/if}
</div>

<style>
  .inv-root { display:flex; flex-direction:column; gap:0.5rem; }
  .grid { display:flex; flex-wrap:wrap; gap:0.5rem; }
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
    align-items: stretch;
    justify-items: center;
  }
  .relics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
    align-items: stretch;
    justify-items: center;
  }
  .item { display:flex; flex-direction:column; align-items:center; font-size:0.75rem; }
  /* Inventory is read-only */
  .item :global(button) { pointer-events:none; }
  .qty { margin-top: 0.25rem; opacity: 0.9; }
</style>
