<script>
  import MenuPanel from './MenuPanel.svelte';
  import { Coins } from 'lucide-svelte';
  import { createEventDispatcher, onMount } from 'svelte';
  import RewardCard from './RewardCard.svelte';
  import CurioChoice from './CurioChoice.svelte';
  import { getCardCatalog, getRelicCatalog } from './api.js';
  import { EFFECT_DESCRIPTIONS, ITEM_EFFECT_MAP } from './effectsInfo.js';

  export let items = [];
  export let gold = 0;
  export let reducedMotion = false;

  const dispatch = createEventDispatcher();
  // Preserve original stock ordering and keep purchased items visible until unload
  let baseList = []; // enriched entries with stable keys
  let awaitingReroll = false;
  let soldKeys = new Set();
  const keyOf = (item) => `${item?.type || 'item'}:${item?.id || ''}:${priceOf(item)}`;
  function buildBaseList(list) {
    const counts = Object.create(null);
    return (list || []).map((raw) => {
      const enriched = enrich(raw);
      const base = keyOf(enriched);
      counts[base] = (counts[base] || 0) + 1;
      const key = `${base}#${counts[base]}`;
      return { ...enriched, key };
    });
  }
  function initBaseOnce() {
    if (!baseList.length && Array.isArray(items) && items.length) {
      baseList = buildBaseList(items);
    }
  }
  function buy(item) {
    // mark this entry as sold (by key) and pass through the purchase
    const k = item?.key || keyOf(item);
    if (k) soldKeys.add(k);
    dispatch('buy', item);
  }
  function reroll() {
    awaitingReroll = true;
    soldKeys = new Set();
    dispatch('reroll');
  }
  function close() {
    baseList = [];
    soldKeys = new Set();
    awaitingReroll = false;
    dispatch('close');
  }

  // Split incoming stock by type and enrich with catalog metadata
  let cardMeta = {};
  let relicMeta = {};
  onMount(async () => {
    try {
      const [cards, relics] = await Promise.all([getCardCatalog(), getRelicCatalog()]);
      cardMeta = Object.fromEntries(cards.map(c => [c.id, c]));
      relicMeta = Object.fromEntries(relics.map(r => [r.id, r]));
    } catch {}
  });

  function priceOf(item) { return Number(item?.price ?? item?.cost ?? 0); }
  // Enrich incoming stock entries with catalog data and presentable about text.
  // For relics, we compute a stable baseAbout to avoid duplicating stack notes
  // during reactive re-enrichment (metadata loads can re-run this).
  function enrich(entry) {
    if (!entry) return entry;
    if (entry.type === 'card') {
      const m = cardMeta[entry.id] || {};
      const baseAbout = entry.about || m.about || '';
      const effectId = ITEM_EFFECT_MAP[entry.id];
      const tooltip = effectId && EFFECT_DESCRIPTIONS[effectId] ? EFFECT_DESCRIPTIONS[effectId] : baseAbout;
      return { ...entry, name: entry.name || m.name || entry.id, stars: entry.stars || m.stars || 1, about: baseAbout, tooltip };
    } else if (entry.type === 'relic') {
      const m = relicMeta[entry.id] || {};
      // Keep a stable baseAbout so reactive re-enrichment doesn't duplicate the suffix
      const baseAbout = entry.baseAbout ?? entry.about ?? m.about ?? '';
      const stacks = typeof entry.stacks === 'number' ? entry.stacks : 0;
      const about = stacks > 0 ? `${baseAbout} (Current stacks: ${stacks})` : baseAbout;
      const effectId = ITEM_EFFECT_MAP[entry.id];
      const tooltip = effectId && EFFECT_DESCRIPTIONS[effectId] ? EFFECT_DESCRIPTIONS[effectId] : baseAbout;
      return { ...entry, name: entry.name || m.name || entry.id, stars: entry.stars || m.stars || 1, baseAbout, about, tooltip };
    }
    return entry;
  }

  // Initialize base list on first stock arrival; replace on reroll
  $: initBaseOnce();
  $: if (awaitingReroll && Array.isArray(items) && items.length) {
    baseList = buildBaseList(items);
    soldKeys = new Set();
    awaitingReroll = false;
  }
  // Keep metadata enrichment reactive for new catalogs
  $: baseList = (baseList, cardMeta, relicMeta, baseList.map((e) => ({ ...enrich(e), key: e.key })));
  // Partition for layout
  $: displayCards = baseList.filter(e => e?.type === 'card');
  $: displayRelics = baseList.filter(e => e?.type === 'relic');
</script>

<MenuPanel data-testid="shop-menu" padding="0.6rem 0.6rem 0.8rem 0.6rem">
  <div class="header">
    <h3>Shop</h3>
    <div class="spacer" />
    <div class="currency" title="Gold">
      <Coins size={16} class={`coin-icon${!reducedMotion ? ' shine' : ''}`} /> {gold}
    </div>
  </div>
  <div class="columns">
    {#if displayCards.length > 0}
      <section class="col">
        <h4>Cards</h4>
        <div class="grid">
          {#each displayCards as item (item.key)}
            <div class={`cell ${soldKeys.has(item.key) ? 'dim sold' : ''}`}>
              <RewardCard entry={item} type="card" disabled={soldKeys.has(item.key)} on:select={() => buy(item)} />
              <div class="buybar">
                <button class="buy" disabled={soldKeys.has(item.key) || priceOf(item) > gold} on:click={() => buy(item)}>
                  {#if soldKeys.has(item.key)}Sold{:else}<Coins size={14} class="coin-icon" /> {priceOf(item)}{/if}
                </button>
              </div>
            </div>
          {/each}
        </div>
      </section>
    {/if}
    <section class="col">
      <h4>Relics</h4>
      {#if displayRelics.length === 0}
        <div class="empty">No relics available.</div>
      {:else}
        <div class="grid">
          {#each displayRelics as item (item.key)}
            <div class={`cell ${soldKeys.has(item.key) ? 'dim sold' : ''}`}>
              <CurioChoice entry={item} disabled={soldKeys.has(item.key)} on:select={() => buy(item)} />
              <div class="buybar">
                <button class="buy" disabled={soldKeys.has(item.key) || priceOf(item) > gold} on:click={() => buy(item)}>
                  {#if soldKeys.has(item.key)}Sold{:else}<Coins size={14} class="coin-icon" /> {priceOf(item)}{/if}
                </button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </section>
  </div>
  <div class="actions">
    <button class="action" on:click={reroll}>Reroll</button>
    <button class="action" on:click={close}>Leave</button>
  </div>
  
</MenuPanel>

<style>
  .header { display:flex; align-items:center; gap:0.5rem; }
  .header h3 { margin: 0; }
  .spacer { flex: 1; }
  .currency { display:flex; align-items:center; gap:0.35rem; }
  .coin-icon { color: #d4af37; }
  .shine { animation: coin-shine 2s linear infinite; }
  @keyframes coin-shine { 0%,100% { filter: brightness(1); } 50% { filter: brightness(1.4); } }

  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }
  .col { display:flex; flex-direction:column; gap:0.5rem; }
  .col h4 { margin: 0; font-size: 1rem; }
  .empty { opacity: 0.8; font-size: 0.9rem; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
    align-items: stretch;
    justify-items: center;
  }
  .cell { position: relative; display:flex; flex-direction:column; align-items:center; transition: opacity 120ms ease, filter 120ms ease; }
  .cell.dim { opacity: 0.55; filter: grayscale(0.2); }
  .cell.sold :global(button.card),
  .cell.sold :global(button.curio) { pointer-events: none; }
  .buybar { margin-top: 0.35rem; }
  .buy { display:flex; align-items:center; gap:0.35rem; border: 1px solid rgba(255,255,255,0.35); background: rgba(0,0,0,0.5); color:#fff; padding: 0.3rem 0.6rem; }
  .buy:disabled { opacity: 0.5; cursor: not-allowed; }

  .actions { display:flex; gap:0.5rem; justify-content:flex-end; margin-top: 0.75rem; }
  .action { border: 1px solid rgba(255,255,255,0.35); background: rgba(0,0,0,0.5); color:#fff; padding: 0.35rem 0.7rem; }

  @media (max-width: 920px) {
    .columns { grid-template-columns: 1fr; }
  }
</style>
