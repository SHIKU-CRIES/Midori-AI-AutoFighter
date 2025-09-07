<script>
  import { onMount } from 'svelte';
  import { getCardCatalog, getRelicCatalog } from '../systems/api.js';
  import CardArt from './CardArt.svelte';
  import CurioChoice from './CurioChoice.svelte';

  export let cards = [];
  export let relics = [];

  // Current tab and selected item state
  let activeTab = 'cards';
  let selectedItem = null;
  
  // Catalog metadata
  let cardMeta = {};
  let relicMeta = {};
  let metaReady = false;

  onMount(async () => {
    try {
      const [cardList, relicList] = await Promise.all([getCardCatalog(), getRelicCatalog()]);
      cardMeta = Object.fromEntries(cardList.map(c => [c.id, c]));
      relicMeta = Object.fromEntries(relicList.map(r => [r.id, r]));
    } catch (e) {
      // Silently ignore; components will fallback to id-only display
    }
    metaReady = true;
  });

  // Helper functions
  const count = (arr) => {
    const map = {};
    for (const id of arr) {
      map[id] = (map[id] || 0) + 1;
    }
    return Object.entries(map);
  };

  const cardStars = (id) => (cardMeta?.[id]?.stars ?? 1) | 0;
  const relicStars = (id) => (relicMeta?.[id]?.stars ?? 1) | 0;
  const cardName = (id) => String(cardMeta?.[id]?.name || id);
  const relicName = (id) => String(relicMeta?.[id]?.name || id);
  const cardDesc = (id) => String(cardMeta?.[id]?.about || 'No description available.');
  const relicDesc = (id) => String(relicMeta?.[id]?.about || 'No description available.');

  // Processed data
  $: cardEntries = count(cards || []);
  $: relicEntries = count(relics || []);

  $: sortedCards = [...cardEntries].sort((a, b) => {
    const [idA] = a; const [idB] = b;
    const s = cardStars(idB) - cardStars(idA);
    if (s !== 0) return s;
    return cardName(idA).localeCompare(cardName(idB));
  });

  $: sortedRelics = [...relicEntries].sort((a, b) => {
    const [idA] = a; const [idB] = b;
    const s = relicStars(idB) - relicStars(idA);
    if (s !== 0) return s;
    return relicName(idA).localeCompare(relicName(idB));
  });

  // Get total counts
  $: cardCount = cards?.length || 0;
  $: relicCount = relics?.length || 0;

  // Star rating colors
  const getStarColor = (stars) => {
    switch(stars) {
      case 5: return '#FFD700'; // Gold
      case 4: return '#9B59B6'; // Purple  
      case 3: return '#3498DB'; // Blue
      case 2: return '#2ECC71'; // Green
      default: return '#95A5A6'; // Gray
    }
  };

  // Item selection
  const selectItem = (id, type, qty = 1) => {
    if (type === 'card') {
      selectedItem = {
        id,
        type: 'card',
        name: cardName(id),
        stars: cardStars(id),
        description: cardDesc(id),
        quantity: qty,
        meta: cardMeta[id]
      };
    } else {
      selectedItem = {
        id,
        type: 'relic',
        name: relicName(id),
        stars: relicStars(id),
        description: relicDesc(id),
        quantity: qty,
        meta: relicMeta[id]
      };
    }
  };

  // Set initial selection when data loads
  $: if (metaReady && !selectedItem) {
    if (activeTab === 'cards' && sortedCards.length > 0) {
      const [id, qty] = sortedCards[0];
      selectItem(id, 'card', qty);
    } else if (activeTab === 'relics' && sortedRelics.length > 0) {
      const [id, qty] = sortedRelics[0];
      selectItem(id, 'relic', qty);
    }
  }

  // Switch tabs
  const switchTab = (tab) => {
    activeTab = tab;
    selectedItem = null;
    // Auto-select first item in new tab
    if (tab === 'cards' && sortedCards.length > 0) {
      const [id, qty] = sortedCards[0];
      selectItem(id, 'card', qty);
    } else if (tab === 'relics' && sortedRelics.length > 0) {
      const [id, qty] = sortedRelics[0];
      selectItem(id, 'relic', qty);
    }
  };
</script>

<div class="star-rail-inventory">
  <!-- Header with tabs -->
  <div class="inventory-header">
    <div class="tab-row">
      <button 
        class="tab" 
        class:active={activeTab === 'cards'}
        on:click={() => switchTab('cards')}
      >
        <span class="tab-icon">🃏</span>
        Cards ({cardCount})
      </button>
      <button 
        class="tab" 
        class:active={activeTab === 'relics'}
        on:click={() => switchTab('relics')}
      >
        <span class="tab-icon">💎</span>
        Relics ({relicCount})
      </button>
    </div>
  </div>

  <div class="inventory-body">
    <!-- Left side: Item grid -->
    <div class="item-grid-container">
      <div class="item-grid">
        {#if activeTab === 'cards'}
          {#each sortedCards as [id, qty]}
            <button 
              class="grid-item" 
              class:selected={selectedItem?.id === id && selectedItem?.type === 'card'}
              on:click={() => selectItem(id, 'card', qty)}
            >
              <div class="item-icon">
                <CardArt entry={{ id, name: cardName(id), stars: cardStars(id), about: cardDesc(id) }} type="card" compact={true} />
              </div>
              <div class="item-quantity">×{qty}</div>
              <div class="item-stars" style="color: {getStarColor(cardStars(id))}">
                {'★'.repeat(cardStars(id))}
              </div>
            </button>
          {/each}
        {:else}
          {#each sortedRelics as [id, qty]}
            <button 
              class="grid-item" 
              class:selected={selectedItem?.id === id && selectedItem?.type === 'relic'}
              on:click={() => selectItem(id, 'relic', qty)}
            >
              <div class="item-icon">
                <CurioChoice entry={{ id, name: relicName(id), stars: relicStars(id), about: relicDesc(id) }} compact={true} />
              </div>
              <div class="item-quantity">×{qty}</div>
              <div class="item-stars" style="color: {getStarColor(relicStars(id))}">
                {'★'.repeat(relicStars(id))}
              </div>
            </button>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Right side: Detail panel -->
    <div class="detail-panel">
      {#if selectedItem}
        <div class="detail-header">
          <h3 class="item-name">{selectedItem.name}</h3>
          <div class="item-meta">
            <div class="item-stars-large" style="color: {getStarColor(selectedItem.stars)}">
              {'★'.repeat(selectedItem.stars)}
            </div>
            <div class="item-quantity-large">×{selectedItem.quantity}</div>
          </div>
        </div>
        
        <div class="detail-preview">
          {#if selectedItem.type === 'card'}
            <CardArt entry={{ 
              id: selectedItem.id, 
              name: selectedItem.name, 
              stars: selectedItem.stars, 
              about: selectedItem.description 
            }} type="card" />
          {:else}
            <CurioChoice entry={{ 
              id: selectedItem.id, 
              name: selectedItem.name, 
              stars: selectedItem.stars, 
              about: selectedItem.description 
            }} />
          {/if}
        </div>

        <div class="detail-description">
          <h4>Description</h4>
          <p>{selectedItem.description}</p>
        </div>

        {#if selectedItem.meta}
          <div class="detail-stats">
            <h4>Details</h4>
            <div class="stats-grid">
              <div class="stat-row">
                <span class="stat-label">Type:</span>
                <span class="stat-value">{selectedItem.type === 'card' ? 'Ability Card' : 'Equipment Relic'}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Rarity:</span>
                <span class="stat-value">{selectedItem.stars} Star</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">ID:</span>
                <span class="stat-value">{selectedItem.id}</span>
              </div>
            </div>
          </div>
        {/if}
      {:else}
        <div class="no-selection">
          <div class="no-selection-icon">📦</div>
          <p>Select an item to view details</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .star-rail-inventory {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 80vh;
    background: var(--glass-bg);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
  }

  .inventory-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.2);
  }

  .tab-row {
    display: flex;
    gap: 0.5rem;
  }

  .tab {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.7);
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .tab.active {
    background: rgba(120,180,255,0.3);
    color: #fff;
    border-color: rgba(120,180,255,0.5);
  }

  .tab:hover:not(.active) {
    background: rgba(255,255,255,0.15);
  }

  .tab-icon {
    font-size: 1.1rem;
  }

  .inventory-body {
    display: flex;
    flex: 1;
    min-height: 0;
  }

  .item-grid-container {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    border-right: 1px solid rgba(255,255,255,0.2);
  }

  .item-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.75rem;
    align-items: start;
  }

  .grid-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .grid-item:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(120,180,255,0.5);
  }

  .grid-item.selected {
    background: rgba(120,180,255,0.2);
    border-color: rgba(120,180,255,0.7);
    box-shadow: 0 0 8px rgba(120,180,255,0.3);
  }

  .item-icon {
    width: 100%;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .item-quantity {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.8);
    margin-top: 0.25rem;
  }

  .item-stars {
    font-size: 0.6rem;
    margin-top: 0.2rem;
  }

  .detail-panel {
    width: 320px;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .detail-header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .item-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #fff;
    margin: 0;
  }

  .item-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .item-stars-large {
    font-size: 1rem;
  }

  .item-quantity-large {
    font-size: 1rem;
    color: rgba(255,255,255,0.8);
    font-weight: 500;
  }

  .detail-preview {
    display: flex;
    justify-content: center;
    padding: 1rem;
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.1);
  }

  .detail-description h4,
  .detail-stats h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
    margin: 0 0 0.5rem 0;
  }

  .detail-description p {
    font-size: 0.9rem;
    line-height: 1.4;
    color: rgba(255,255,255,0.8);
    margin: 0;
  }

  .stats-grid {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
  }

  .stat-label {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
  }

  .stat-value {
    font-size: 0.85rem;
    color: #fff;
    font-weight: 500;
  }

  .no-selection {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(255,255,255,0.5);
    text-align: center;
  }

  .no-selection-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  @media (max-width: 768px) {
    .inventory-body {
      flex-direction: column;
    }
    
    .detail-panel {
      width: 100%;
      border-top: 1px solid rgba(255,255,255,0.2);
      border-right: none;
    }
    
    .item-grid-container {
      border-right: none;
    }
  }
</style>