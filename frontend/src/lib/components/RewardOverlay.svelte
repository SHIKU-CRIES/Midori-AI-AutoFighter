<script>
  import { createEventDispatcher, onMount } from 'svelte';
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

  // Render immediately; CSS animations handle reveal on mount
  onMount(() => {});

  function titleForItem(item) {
    if (!item) return '';
    if (item.name) return item.name;
    if (item.id === 'ticket') return 'Gacha Ticket';
    const id = String(item.id || '').toLowerCase();
    const cap = id.charAt(0).toUpperCase() + id.slice(1);
    const stars = Number.isFinite(item.stars) ? String(item.stars) : '';
    return stars ? `${cap} Upgrade (${stars})` : `${cap} Upgrade`;
  }

  let cardsDone = false;
  let showNextButton = false;
  $: showCards = cards.length > 0 && !cardsDone;
  $: showRelics = relics.length > 0 && (cards.length === 0 || cardsDone);
  $: remaining = (showCards ? cards.length : 0) + (showRelics ? relics.length : 0);

  function handleSelect(e) {
    const detail = e.detail || {};
    if (detail.type === 'card') {
      cardsDone = true;
    }
    dispatch('select', detail);
  }

  // Auto-advance when there are no selectable rewards and no visible loot/gold.
  // This avoids showing an empty rewards popup in loot-consumed cases.
  let autoTimer;
  $: {
    clearTimeout(autoTimer);
    const noChoices = remaining === 0;
    const noLoot = (!gold || gold <= 0) && (!Array.isArray(items) || items.length === 0);
    if (noChoices && noLoot) {
      autoTimer = setTimeout(() => dispatch('next'), 5000);
    }
  }
  // Cleanup timer on unmount
  import { onDestroy } from 'svelte';
  onDestroy(() => clearTimeout(autoTimer));

  // Show Next Room button when there's loot but no choices
  $: {
    const noChoices = remaining === 0;
    const hasLoot = (gold > 0) || (Array.isArray(items) && items.length > 0);
    showNextButton = noChoices && hasLoot;
  }

  function handleNextRoom() {
    dispatch('nextRoom'); // Changed from 'next' to 'nextRoom' to match expected event
  }
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
  /* CSS-based reveal: slide the whole card, twinkles appear first, then card fades in */
  @keyframes overlay-slide {
    0%   { transform: translateY(-40px); }
    100% { transform: translateY(0); }
  }
  /* Twinkles fade in early to "form" the card */
  @keyframes overlay-twinkle-fade {
    0%   { opacity: 0; }
    20%  { opacity: 0.6; }
    40%  { opacity: 1; }
    100% { opacity: 1; }
  }
  /* Card content fades in later than twinkles */
  @keyframes overlay-card-fade {
    0%   { opacity: 0; }
    30%  { opacity: 0; }
    100% { opacity: 1; }
  }
  .reveal {
    animation: overlay-slide 360ms cubic-bezier(0.22, 1, 0.36, 1) both;
    animation-delay: var(--delay, 0ms);
  }
  /* Target the CardArt twinkles layer only */
  .reveal :global(.twinkles) {
    opacity: 0;
    animation: overlay-twinkle-fade 520ms cubic-bezier(0.22, 1, 0.36, 1) both;
    animation-delay: var(--delay, 0ms);
  }
  /* Fade in the card content (including photo/box) slightly after twinkles */
  .reveal :global(.card-art) {
    opacity: 0;
    animation: overlay-card-fade 520ms cubic-bezier(0.22, 1, 0.36, 1) both;
    animation-delay: var(--delay, 0ms);
  }

  .next-button {
    margin-top: 1rem;
    padding: 0.75rem 2rem;
    background: linear-gradient(145deg, #4a90e2, #357abd);
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: all 0.2s ease;
  }

  .next-button:hover {
    background: linear-gradient(145deg, #5ba0f2, #4a90e2);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
  }

  .next-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  
</style>

<div class="layout">
  {#if showCards}
  <h3 class="section-title">Choose a Card</h3>
  <div class="choices">
        {#each cards.slice(0,3) as card, i (card.id)}
          <div class="reveal" style={`--delay: ${i * 120}ms`}>
            <RewardCard entry={card} type="card" on:select={handleSelect} />
          </div>
        {/each}
    </div>
  {/if}
  {#if showRelics}
  <h3 class="section-title">Choose a Relic</h3>
  <div class="choices">
        {#each relics.slice(0,3) as relic, i (relic.id)}
          <div class="reveal" style={`--delay: ${i * 120}ms`}>
            <CurioChoice entry={relic} on:select={handleSelect} />
          </div>
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
  
  {#if showNextButton}
    <button class="next-button" on:click={handleNextRoom}>Next Room</button>
  {/if}
  <!-- Auto-advance remains when no choices/loot -->
</div>
