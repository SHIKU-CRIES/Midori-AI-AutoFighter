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
        // Extract buffs from passives and other effects
        const buffs = [];
        if (character.passives) {
          character.passives.forEach(passive => {
            if (typeof passive === 'object' && passive.name) {
              // Check if it's a positive effect (rough heuristic)
              if (passive.name.toLowerCase().includes('buff') || 
                  passive.name.toLowerCase().includes('boost') ||
                  passive.name.toLowerCase().includes('enhance')) {
                buffs.push({
                  name: passive.name,
                  id: passive.id || passive.name,
                  duration: passive.duration || passive.turns_left || 'Permanent',
                  description: passive.description || 'Beneficial effect',
                  source: 'passive'
                });
              }
            }
          });
        }
        // Add stat modifiers that are positive
        if (character.mods) {
          character.mods.forEach(mod => {
            if (typeof mod === 'object' && mod.name) {
              buffs.push({
                name: mod.name,
                id: mod.id || mod.name,
                duration: mod.turns || 'Permanent',
                description: mod.description || 'Stat modification',
                source: 'modifier'
              });
            }
          });
        }
        return buffs;
      case 'debuffs':
        // Extract debuffs from effects
        const debuffs = [];
        if (character.passives) {
          character.passives.forEach(passive => {
            if (typeof passive === 'object' && passive.name) {
              // Check if it's a negative effect
              if (passive.name.toLowerCase().includes('debuff') ||
                  passive.name.toLowerCase().includes('curse') ||
                  passive.name.toLowerCase().includes('weaken')) {
                debuffs.push({
                  name: passive.name,
                  id: passive.id || passive.name,
                  duration: passive.duration || passive.turns_left || 'Permanent',
                  description: passive.description || 'Harmful effect',
                  source: 'passive'
                });
              }
            }
          });
        }
        return debuffs;
      case 'relics':
        // Get relic effects from battleSnapshot if available
        if (battleSnapshot && battleSnapshot.relics) {
          return battleSnapshot.relics.map(relicId => ({
            name: relicId,
            id: relicId,
            duration: 'Permanent',
            description: 'Relic effect active',
            source: 'relic'
          }));
        }
        return [];
      case 'cards':
        // Get card effects from battleSnapshot if available
        if (battleSnapshot && battleSnapshot.cards) {
          return battleSnapshot.cards.map(cardId => ({
            name: cardId,
            id: cardId,
            duration: 'Permanent',
            description: 'Card effect active',
            source: 'card'
          }));
        }
        return [];
      case 'passives':
        if (character.passives) {
          return character.passives.map(passive => {
            if (typeof passive === 'string') {
              return {
                name: passive,
                id: passive,
                duration: 'Permanent',
                description: 'Passive ability',
                source: 'passive'
              };
            }
            return {
              name: passive.name || passive.id || 'Unknown',
              id: passive.id || passive.name || 'unknown',
              duration: passive.duration || passive.turns_left || 'Permanent',
              description: passive.description || 'Passive ability',
              source: 'passive'
            };
          });
        }
        return [];
      default:
        return [];
    }
  }

  function formatDuration(effect) {
    if (effect.duration !== undefined) {
      if (typeof effect.duration === 'number') {
        return effect.duration > 0 ? `${effect.duration} turns left` : 'Expired';
      }
      return String(effect.duration);
    }
    if (effect.turns_left !== undefined) {
      return `${effect.turns_left} turns left`;
    }
    if (effect.turns !== undefined) {
      return `${effect.turns} turns left`;
    }
    return 'Permanent';
  }

  function formatEffect(effect) {
    let description = effect.name || effect.id || 'Unknown Effect';
    
    // Add amount/damage information
    if (effect.amount !== undefined) {
      description += ` (${effect.amount} per turn)`;
    } else if (effect.damage !== undefined) {
      description += ` (${effect.damage} damage/turn)`;
    } else if (effect.healing !== undefined) {
      description += ` (${effect.healing} healing/turn)`;
    }
    
    return description;
  }

  function getEffectDetails(effect) {
    const details = [];
    
    if (effect.description) {
      details.push(`Description: ${effect.description}`);
    }
    
    if (effect.amount !== undefined) {
      details.push(`Amount per turn: ${effect.amount}`);
    }
    
    if (effect.damage !== undefined) {
      details.push(`Damage per turn: ${effect.damage}`);
    }
    
    if (effect.healing !== undefined) {
      details.push(`Healing per turn: ${effect.healing}`);
    }
    
    if (effect.source) {
      details.push(`Source: ${effect.source}`);
    }
    
    // Calculate total damage/healing potential
    if (effect.damage && effect.duration && typeof effect.duration === 'number') {
      const totalDamage = effect.damage * effect.duration;
      details.push(`Total potential damage: ${totalDamage}`);
    }
    
    if (effect.healing && effect.duration && typeof effect.duration === 'number') {
      const totalHealing = effect.healing * effect.duration;
      details.push(`Total potential healing: ${totalHealing}`);
    }
    
    return details;
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
          <div class="character-type">
            {selectedCharacter.type === 'player' ? 'Party Member' : 'Foe'}
          </div>
          
          <div class="stats-grid">
            <div class="stat-section">
              <h4>Health</h4>
              <div class="stat">
                <label>HP:</label>
                <span>{selectedCharacter.hp}/{selectedCharacter.max_hp || selectedCharacter.hp}</span>
              </div>
              {#if selectedCharacter.shield}
                <div class="stat">
                  <label>Shield:</label>
                  <span>{selectedCharacter.shield}</span>
                </div>
              {/if}
            </div>

            <div class="stat-section">
              <h4>Combat Stats</h4>
              <div class="stat">
                <label>Attack:</label>
                <span>{selectedCharacter.attack || selectedCharacter.atk || 0}</span>
              </div>
              <div class="stat">
                <label>Defense:</label>
                <span>{selectedCharacter.defense || selectedCharacter.def || 0}</span>
              </div>
              {#if selectedCharacter.crit_rate !== undefined}
                <div class="stat">
                  <label>Crit Rate:</label>
                  <span>{(selectedCharacter.crit_rate * 100).toFixed(1)}%</span>
                </div>
              {/if}
              {#if selectedCharacter.mitigation !== undefined}
                <div class="stat">
                  <label>Mitigation:</label>
                  <span>{selectedCharacter.mitigation}</span>
                </div>
              {/if}
            </div>

            <div class="stat-section">
              <h4>Battle Performance</h4>
              <div class="stat">
                <label>Damage Dealt:</label>
                <span>{selectedCharacter.damage_dealt || 0}</span>
              </div>
              <div class="stat">
                <label>Damage Taken:</label>
                <span>{selectedCharacter.damage_taken || 0}</span>
              </div>
              {#if selectedCharacter.kills !== undefined}
                <div class="stat">
                  <label>Kills:</label>
                  <span>{selectedCharacter.kills}</span>
                </div>
              {/if}
              {#if selectedCharacter.healing_done !== undefined}
                <div class="stat">
                  <label>Healing Done:</label>
                  <span>{selectedCharacter.healing_done}</span>
                </div>
              {/if}
            </div>

            {#if selectedCharacter.element || selectedCharacter.damage_type}
              <div class="stat-section">
                <h4>Element</h4>
                <div class="stat">
                  <label>Type:</label>
                  <span class="element-type">{selectedCharacter.element || selectedCharacter.damage_type || 'Generic'}</span>
                </div>
              </div>
            {/if}
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
                <div class="effect-header">
                  <div class="effect-name">{formatEffect(effect)}</div>
                  <div class="effect-duration">{formatDuration(effect)}</div>
                </div>
                <div class="effect-details">
                  {#each getEffectDetails(effect) as detail}
                    <div class="effect-detail">{detail}</div>
                  {/each}
                </div>
              </div>
            {:else}
              <div class="no-effects">
                <p>No {tabs.find(t => t.id === activeTab)?.label.toLowerCase()} effects</p>
              </div>
            {/each}
          {:else}
            <div class="no-effects">
              <p>Select a character to view effects</p>
            </div>
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
    max-height: 500px;
    overflow-y: auto;
  }

  .character-type {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stats-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .stat-section {
    background: rgba(255, 255, 255, 0.05);
    padding: 0.75rem;
    border-radius: 3px;
  }

  .stat-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #fff;
    opacity: 0.8;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding-bottom: 0.25rem;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    font-size: 0.9rem;
  }

  .stat label {
    font-weight: bold;
    opacity: 0.9;
  }

  .stat span {
    opacity: 0.8;
  }

  .element-type {
    text-transform: capitalize;
    color: #4fc3f7;
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

  .effect-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .effect-name {
    font-weight: bold;
    flex: 1;
    margin-right: 0.5rem;
  }

  .effect-duration {
    font-size: 0.8rem;
    opacity: 0.8;
    white-space: nowrap;
  }

  .effect-details {
    margin-top: 0.5rem;
  }

  .effect-detail {
    font-size: 0.8rem;
    line-height: 1.3;
    margin-bottom: 0.25rem;
    opacity: 0.9;
  }

  .no-effects {
    text-align: center;
    margin: 2rem 0;
    opacity: 0.8;
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