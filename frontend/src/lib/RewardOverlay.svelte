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
    display: grid;
    grid-template-columns: 1fr minmax(240px, 360px);
    gap: 0.8rem;
    align-items: flex-start;
  }

  .reward {
    width: fit-content;
    height: fit-content;
  }

  .choice-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .status {
    margin-top: 0.5rem;
    text-align: left;
  }
  .status ul {
    margin: 0.25rem 0;
    padding-left: 1rem;
    text-align: left;
  }

  .stats {
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
    padding: 0.5rem;
    color: #fff;
    font-size: 0.85rem;
  }
  .stats table {
    width: 100%;
    border-collapse: collapse;
  }
  .stats th,
  .stats td {
    padding: 0.25rem 0.5rem;
    text-align: left;
  }
  .stats th {
    border-bottom: 1px solid rgba(255,255,255,0.2);
  }
  .stats td {
    border-bottom: 1px solid rgba(255,255,255,0.1);
  }
</style>

<div class="layout">
  <div class="reward">
    {#if cards.length}
      <h3>Choose a Card</h3>
      <div class="choice-row">
        {#each cards.slice(0,3) as card}
          <RewardCard entry={card} type="card" on:click={() => dispatch('select', { type: 'card', id: card.id })} />
        {/each}
      </div>
    {/if}
    {#if relics.length}
      <h3>Choose a Relic</h3>
      <div class="choice-row">
        {#each relics.slice(0,3) as relic}
          <CurioChoice entry={relic} on:click={() => dispatch('select', { type: 'relic', id: relic.id })} />
        {/each}
      </div>
    {/if}
    {#if items.length}
      <h3>Drops</h3>
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
      <button on:click={() => dispatch('next')} disabled={remaining > 0}>
        {ended ? 'End Run' : 'Next Room'}
      </button>
    </div>
  </div>
  <div class="stats">
    <table>
      <thead>
        <tr>
          <th>Member</th>
          <th>Dmg Dealt</th>
          <th>Dmg Taken</th>
          <th>Healing</th>
        </tr>
      </thead>
      <tbody>
        {#each partyStats as member}
          <tr>
            <td>{member.name}</td>
            <td>{member.damage_dealt ?? 0}</td>
            <td>-</td>
            <td>-</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
