<script>
  import { createEventDispatcher } from 'svelte';
  import RewardCard from './RewardCard.svelte';
  import CurioChoice from './CurioChoice.svelte';

  export let cards = [];
  export let relics = [];
  export let items = [];
  export let gold = 0;
  export let partyStats = [];
  export let ended = false;
  export let nextRoom = '';

  const dispatch = createEventDispatcher();

  function titleForItem(item) {
    if (!item) return '';
    if (item.name) return item.name;
    if (item.id === 'ticket') return 'Gacha Ticket';
    const id = String(item.id || '').toLowerCase();
    const cap = id.charAt(0).toUpperCase() + id.slice(1);
    const stars = Number.isFinite(item.stars) ? String(item.stars) : '';
    return stars ? `${cap} Upgrade (${stars})` : `${cap} Upgrade`;
  }

  $: remaining = cards.length + relics.length;
</script>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .section-title {
    margin: 0.25rem 0 0.5rem;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }

  .choices {
    display: grid;
    grid-template-columns: repeat(3, minmax(200px, 1fr));
    gap: 0.75rem;
    align-items: stretch;
    justify-items: center;
    width: 100%;
    max-width: 960px;
  }

  .status {
    margin-top: 0.25rem;
    text-align: center;
    color: #ddd;
  }
  .status ul {
    display: inline-block;
    margin: 0.25rem 0;
    padding-left: 1rem;
    text-align: left;
  }
</style>

<div class="layout">
  {#if cards.length}
    <h3 class="section-title">Choose a Card</h3>
    <div class="choices">
        {#each cards.slice(0,3) as card}
          <RewardCard entry={card} type="card" on:select={(e) => dispatch('select', e.detail)} />
        {/each}
    </div>
  {/if}
  {#if relics.length}
    <h3 class="section-title">Choose a Relic</h3>
    <div class="choices">
        {#each relics.slice(0,3) as relic}
          <CurioChoice entry={relic} on:select={(e) => dispatch('select', e.detail)} />
        {/each}
    </div>
  {/if}
  {#if items.length}
    <h3 class="section-title">Drops</h3>
    <div class="status">
      <ul>
        {#each items as item}
          <li>{titleForItem(item)}</li>
        {/each}
      </ul>
    </div>
  {/if}
  {#if gold}
    <div class="status">Gold +{gold}</div>
  {/if}
  <div class="status">
    <button class="icon-btn" on:click={() => dispatch('next')} disabled={remaining > 0}>
      {ended ? 'End Run' : 'Next Room'}
    </button>
  </div>
</div>
