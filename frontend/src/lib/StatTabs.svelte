<script>
  import { getElementIcon, getElementColor } from './assetLoader.js';
  import { createEventDispatcher } from 'svelte';

  /**
   * Renders the stats panel with category tabs and a toggle control.
   *
   * Props:
   * - roster: array of character objects
   * - previewId: ID of character to show stats for
   * - selected: array of selected character IDs
   *
   * Events:
   * - toggle: dispatched with the previewId when Add/Remove is clicked
   */
  export let roster = [];
  export let previewId;
  export let selected = [];

  const statTabs = ['Core', 'Offense', 'Defense'];
  let activeTab = 'Core';
  const dispatch = createEventDispatcher();

  function toggleMember() {
    if (!previewId) return;
    dispatch('toggle', previewId);
  }
</script>

<div class="stats-panel" data-testid="stats-panel">
  <div class="stats-tabs">
    {#each statTabs as tab}
      <button class="tab-btn" class:active={activeTab === tab} on:click={() => activeTab = tab}>
        {tab}
      </button>
    {/each}
  </div>
  {#if previewId}
    {#each roster.filter(r => r.id === previewId) as sel}
      <div class="stats-header">
        <span class="char-name">{sel.name}</span>
        <span class="char-level">Lv {sel.stats.level}</span>
        <svelte:component
          this={getElementIcon(sel.element)}
          class="type-icon"
          style={`color: ${getElementColor(sel.element)}`}
          aria-hidden="true" />
      </div>
      <div class="stats-list">
        {#if activeTab === 'Core'}
          <div><span>HP</span><span>{sel.stats.hp ?? '-'}</span></div>
          <div><span>EXP</span><span>{sel.stats.exp ?? sel.stats.xp ?? '-'}</span></div>
          <div><span>Vitality</span><span>{sel.stats.vitality ?? sel.stats.vita ?? '-'}</span></div>
          <div><span>Regain</span><span>{sel.stats.regain ?? sel.stats.regain_rate ?? '-'}</span></div>
        {:else if activeTab === 'Offense'}
          <div><span>ATK</span><span>{sel.stats.atk ?? '-'}</span></div>
          <div><span>CRIT Rate</span><span>{(sel.stats.critRate ?? sel.stats.crit_rate ?? 0) + '%'}</span></div>
          <div><span>CRIT DMG</span><span>{(sel.stats.critDamage ?? sel.stats.crit_damage ?? 0) + '%'}</span></div>
          <div><span>Effect Hit Rate</span><span>{(sel.stats.effectHit ?? sel.stats.effect_hit_rate ?? 0) + '%'}</span></div>
        {:else if activeTab === 'Defense'}
          <div><span>DEF</span><span>{sel.stats.defense ?? '-'}</span></div>
          <div><span>Mitigation</span><span>{sel.stats.mitigation ?? '-'}</span></div>
          <div><span>Dodge Odds</span><span>{sel.stats.dodge_odds ?? '-'}</span></div>
          <div><span>Effect Resist</span><span>{sel.stats.effectResist ?? sel.stats.effect_resistance ?? '-'}</span></div>
        {/if}
      </div>
    {/each}
  {:else}
    <div class="stats-placeholder">Select a character to view stats</div>
  {/if}
  {#if previewId}
    <div class="stats-confirm">
      <button class="confirm" on:click={toggleMember}>
        {selected.includes(previewId) ? 'Remove from party' : 'Add to party'}
      </button>
    </div>
  {/if}
</div>

<style>
.stats-panel {
  flex: 1;
  width: 350px;
  background: rgba(0,0,0,0.25);
  border-left: 2px solid #444;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
  border-radius: 8px;
}
.stats-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  padding-bottom: 0.5rem;
}
.char-name { font-size: 1.2rem; color: #fff; flex: 1; }
.char-level { font-size: 1rem; color: #ccc; }
.type-icon { width: 24px; height: 24px; }
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.stats-list div { display: flex; justify-content: space-between; color: #ddd; }
.stats-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-style: italic;
}
.stats-confirm {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  min-height: 32px;
  padding: 0.15rem 0;
  margin-top: 0.25rem;
}
button.confirm {
  border: 1.5px solid #fff;
  background: transparent;
  color: #fff;
  padding: 0.12rem 0.4rem;
  align-self: flex-end;
  font-size: 0.95rem;
  min-height: 28px;
  border-radius: 6px;
}
.stats-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.tab-btn {
  background: rgba(255,255,255,0.1);
  color: #ddd;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}
.tab-btn.active { background: rgba(255,255,255,0.3); color: #fff; }
</style>
