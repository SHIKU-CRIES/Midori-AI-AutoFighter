<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import FighterPortrait from './battle/FighterPortrait.svelte';
  import RewardCard from './RewardCard.svelte';
  import CurioChoice from './CurioChoice.svelte';
  import { getElementColor } from './assetLoader.js';
  import { getBattleSummary } from './runApi.js';

  export let runId = '';
  export let battleIndex = 0;
  export let cards = [];
  export let relics = [];
  export let party = [];
  export let foes = [];

  const dispatch = createEventDispatcher();
  let summary = { damage_by_type: {} };

  const elements = ['Generic', 'Light', 'Dark', 'Wind', 'Lightning', 'Fire', 'Ice'];

  // Prefer room-provided ids; if no bar data is available for them, fall back
  // to the ids present in the fetched summary to ensure graphs are shown.
  let partyDisplay = [];
  let foesDisplay = [];
  $: partyDisplay = (party && party.length ? party : (summary.party_members || []));
  $: foesDisplay = (foes && foes.length ? foes : (summary.foes || []));

  onMount(async () => {
    if (!runId || !battleIndex) return;
    let cancelled = false;
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    async function loadWithRetry() {
      for (let attempt = 0; attempt < 10 && !cancelled; attempt++) {
        try {
          const res = await getBattleSummary(runId, battleIndex);
          summary = res || { damage_by_type: {} };
          return;
        } catch (err) {
          // 404 is expected briefly while the backend writes logs
          if (err?.status !== 404) {
            console.warn('Battle summary fetch failed', err?.message || err);
            return;
          }
        }
        await sleep(attempt < 5 ? 400 : 800);
      }
    }
    loadWithRetry();
    return () => { cancelled = true; };
  });

  function barData(id) {
    const totals = summary.damage_by_type?.[id] || {};
    const total = Object.values(totals).reduce((a, b) => a + b, 0) || 1;
    return elements
      .map((el) => ({ element: el, pct: ((totals[el] || 0) / total) * 100 }))
      .filter((seg) => seg.pct > 0);
  }

  function primaryElement(id) {
    const totals = summary.damage_by_type?.[id] || {};
    const entries = Object.entries(totals);
    if (entries.length === 0) return 'Generic';
    return entries.sort((a, b) => b[1] - a[1])[0][0];
  }

  function handleSelect(e) {
    dispatch('select', e.detail);
  }

  // If no bars for provided ids but summary has data for others, switch display ids
  $: {
    const hasAnyBars = (ids) => Array.isArray(ids) && ids.some((id) => barData(id).length > 0);
    const summaryParty = summary?.party_members || [];
    const summaryFoes = summary?.foes || [];
    if (!hasAnyBars(partyDisplay) && hasAnyBars(summaryParty)) partyDisplay = summaryParty;
    if (!hasAnyBars(foesDisplay) && hasAnyBars(summaryFoes)) foesDisplay = summaryFoes;
  }
</script>

<style>
  .layout {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
  }
  .side {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .combatant {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .bars {
    display: flex;
    width: var(--portrait-size, 6rem);
    height: 0.5rem;
    margin-top: 0.25rem;
  }
  .bar {
    height: 100%;
  }
  .rewards {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
  .reward-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(200px, 1fr));
    gap: 0.75rem;
    max-width: 960px;
  }
</style>

<div class="layout">
  <div class="side">
    {#each partyDisplay as member}
      <div class="combatant">
        <FighterPortrait
          fighter={{ id: member, element: primaryElement(member), hp: 1, max_hp: 1 }}
        />
        <div class="bars">
          {#each barData(member) as seg}
            <div
              class="bar"
              style={`width: ${seg.pct}%; background: ${getElementColor(seg.element)}`}
            />
          {/each}
        </div>
      </div>
    {/each}
  </div>
  <div class="side rewards">
    {#if cards.length}
      <div class="reward-grid">
        {#each cards.slice(0,3) as card, i (card.id)}
          <RewardCard entry={card} type="card" on:select={handleSelect} />
        {/each}
      </div>
    {/if}
    {#if relics.length}
      <div class="reward-grid">
        {#each relics.slice(0,3) as relic, i (relic.id)}
          <CurioChoice entry={relic} on:select={handleSelect} />
        {/each}
      </div>
    {/if}
  </div>
  <div class="side">
    {#each foesDisplay as foe}
      <div class="combatant">
        <FighterPortrait
          fighter={{ id: foe, element: primaryElement(foe), hp: 1, max_hp: 1 }}
        />
        <div class="bars">
          {#each barData(foe) as seg}
            <div
              class="bar"
              style={`width: ${seg.pct}%; background: ${getElementColor(seg.element)}`}
            />
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>
