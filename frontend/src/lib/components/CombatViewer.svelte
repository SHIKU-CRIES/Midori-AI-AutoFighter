<!--
  CombatViewer.svelte
  Displays detailed combat information with pause/resume functionality.
  Shows character lists, stats, and status effects in a 3-part layout.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import MenuPanel from './MenuPanel.svelte';

  export let party = [];
  export let foes = [];
  export let runId = '';
  export let battleSnapshot = null;

  const dispatch = createEventDispatcher();

  let selectedCharacterId = null;
  let activeTab = 'dots';

  // Character selection
  $: allCharacters = [
    ...party.map(p => ({ ...p, type: 'player' })),
    ...foes.map(f => ({ ...f, type: 'foe' }))
  ];

  $: selectedCharacter = allCharacters.find(c => c.id === selectedCharacterId) || allCharacters[0];

  // Status effect tabs
  const tabs = [
    { id: 'dots', label: 'DoTs' },
    { id: 'hots', label: 'HoTs' },
    { id: 'buffs', label: 'Buffs' },
    { id: 'debuffs', label: 'Debuffs' },
    { id: 'relics', label: 'Relics' },
    { id: 'cards', label: 'Cards' },
    { id: 'passives', label: 'Passives' }
  ];

  function getStatusEffects(character, type) {
    if (!character) return [];
    
    switch (type) {
      case 'dots':
        return character.dots || [];
      case 'hots':
        return character.hots || [];
      case 'buffs':
        // Extract buffs from other effect arrays if needed
        return [];
      case 'debuffs':
        // Extract debuffs from other effect arrays if needed
        return [];
      case 'relics':
        // Need to get relic effects for this character
        return [];
      case 'cards':
        // Need to get card effects for this character
        return [];
      case 'passives':
        return character.passives || [];
      default:
        return [];
    }
  }

  function formatDuration(effect) {
    if (effect.duration !== undefined) {
      return `${effect.duration} turns left`;
    }
    if (effect.turns_left !== undefined) {
      return `${effect.turns_left} turns left`;
    }
    return 'Permanent';
  }

  function formatEffect(effect) {
    let description = effect.name || effect.id || 'Unknown Effect';
    
    if (effect.amount) {
      description += ` (${effect.amount} per turn)`;
    }
    
    return description;
  }

  // Handle pause when component mounts
  import { onMount, onDestroy } from 'svelte';
  
  onMount(() => {
    dispatch('pauseCombat');
  });

  onDestroy(() => {
    dispatch('resumeCombat');
  });

  function handleClose() {
    dispatch('close');
  }
</script>

<MenuPanel>
  <div class="combat-viewer">
    <div class="viewer-header">
      <h2>Combat Viewer</h2>
      <button class="close-btn" on:click={handleClose}>×</button>
    </div>
    
    <div class="viewer-content">
      <!-- Left panel: Character list -->
      <div class="character-list">
        <h3>Characters</h3>
        
        <div class="character-section">
          <h4>Party</h4>
          {#each party as character}
            <button 
              class="character-item" 
              class:selected={selectedCharacterId === character.id}
              on:click={() => selectedCharacterId = character.id}
            >
              <div class="character-name">{character.id}</div>
              <div class="character-stats">
                HP: {character.hp}/{character.max_hp || character.hp}
              </div>
            </button>
          {/each}
        </div>

        <div class="character-section">
          <h4>Foes</h4>
          {#each foes as character}
            <button 
              class="character-item" 
              class:selected={selectedCharacterId === character.id}
              on:click={() => selectedCharacterId = character.id}
            >
              <div class="character-name">{character.id}</div>
              <div class="character-stats">
                HP: {character.hp}/{character.max_hp || character.hp}
              </div>
            </button>
          {/each}
        </div>
      </div>

      <!-- Center panel: Character details -->
      <div class="character-details">
        {#if selectedCharacter}
          <h3>{selectedCharacter.id}</h3>
          <div class="stats-grid">
            <div class="stat">
              <label>HP:</label>
              <span>{selectedCharacter.hp}/{selectedCharacter.max_hp || selectedCharacter.hp}</span>
            </div>
            <div class="stat">
              <label>Attack:</label>
              <span>{selectedCharacter.attack || selectedCharacter.atk || 0}</span>
            </div>
            <div class="stat">
              <label>Defense:</label>
              <span>{selectedCharacter.defense || selectedCharacter.def || 0}</span>
            </div>
            <div class="stat">
              <label>Damage Dealt:</label>
              <span>{selectedCharacter.damage_dealt || 0}</span>
            </div>
            <div class="stat">
              <label>Damage Taken:</label>
              <span>{selectedCharacter.damage_taken || 0}</span>
            </div>
          </div>
        {:else}
          <p>Select a character to view details</p>
        {/if}
      </div>

      <!-- Right panel: Status effects -->
      <div class="status-effects">
        <div class="tab-header">
          {#each tabs as tab}
            <button 
              class="tab-btn" 
              class:active={activeTab === tab.id}
              on:click={() => activeTab = tab.id}
            >
              {tab.label}
            </button>
          {/each}
        </div>

        <div class="tab-content">
          {#if selectedCharacter}
            {#each getStatusEffects(selectedCharacter, activeTab) as effect}
              <div class="effect-item">
                <div class="effect-name">{formatEffect(effect)}</div>
                <div class="effect-duration">{formatDuration(effect)}</div>
                {#if effect.description}
                  <div class="effect-description">{effect.description}</div>
                {/if}
              </div>
            {:else}
              <p>No {tabs.find(t => t.id === activeTab)?.label.toLowerCase()} effects</p>
            {/each}
          {:else}
            <p>Select a character to view effects</p>
          {/if}
        </div>
      </div>
    </div>
  </div>
</MenuPanel>

<style>
  .combat-viewer {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .close-btn {
    background: none;
    border: none;
    color: #fff;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
  }

  .viewer-content {
    display: flex;
    flex: 1;
    gap: 1rem;
    padding: 1rem;
  }

  .character-list {
    flex: 1;
    min-width: 200px;
  }

  .character-section {
    margin-bottom: 1rem;
  }

  .character-section h4 {
    margin: 0 0 0.5rem 0;
    color: #fff;
    font-size: 0.9rem;
    opacity: 0.8;
  }

  .character-item {
    width: 100%;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    padding: 0.5rem;
    margin-bottom: 0.25rem;
    cursor: pointer;
    text-align: left;
  }

  .character-item:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .character-item.selected {
    background: rgba(120, 180, 255, 0.3);
    border-color: rgba(120, 180, 255, 0.5);
  }

  .character-name {
    font-weight: bold;
    font-size: 0.9rem;
  }

  .character-stats {
    font-size: 0.8rem;
    opacity: 0.8;
  }

  .character-details {
    flex: 1;
    min-width: 250px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }

  .stat label {
    font-weight: bold;
  }

  .status-effects {
    flex: 1;
    min-width: 300px;
  }

  .tab-header {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 1rem;
  }

  .tab-btn {
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    cursor: pointer;
    font-size: 0.8rem;
  }

  .tab-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .tab-btn.active {
    background: rgba(120, 180, 255, 0.3);
    border-color: rgba(120, 180, 255, 0.5);
  }

  .tab-content {
    max-height: 400px;
    overflow-y: auto;
  }

  .effect-item {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 3px;
  }

  .effect-name {
    font-weight: bold;
    margin-bottom: 0.25rem;
  }

  .effect-duration {
    font-size: 0.8rem;
    opacity: 0.8;
    margin-bottom: 0.25rem;
  }

  .effect-description {
    font-size: 0.8rem;
    line-height: 1.3;
  }

  h2, h3 {
    color: #fff;
    margin: 0 0 1rem 0;
  }

  h3 {
    font-size: 1.1rem;
  }

  p {
    color: #fff;
    opacity: 0.8;
    text-align: center;
    margin: 2rem 0;
  }
</style>