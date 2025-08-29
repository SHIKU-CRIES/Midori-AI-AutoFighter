<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import FighterPortrait from './battle/FighterPortrait.svelte';
  import RewardCard from './RewardCard.svelte';
  import CurioChoice from './CurioChoice.svelte';
  import { getElementColor } from './assetLoader.js';

  export let runId = '';
  export let battleIndex = 0;
  export let cards = [];
  export let relics = [];
  export let party = [];
  export let foes = [];

  const dispatch = createEventDispatcher();
  let summary = { damage_by_type: {} };

  const elements = ['Generic', 'Light', 'Dark', 'Wind', 'Lightning', 'Fire', 'Ice'];

  onMount(async () => {
    if (!runId || !battleIndex) return;
    try {
      const res = await fetch(`/run/${runId}/battles/${battleIndex}/summary`);
      summary = await res.json();
    } catch (err) {
      console.error('Failed to load summary', err);
    }
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
    {#each party as member}
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
    {#each foes as foe}
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

