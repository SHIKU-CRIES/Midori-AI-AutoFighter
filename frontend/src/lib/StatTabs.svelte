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

  const statTabs = ['Core', 'Offense', 'Defense', 'Effects'];
  let activeTab = 'Core';
  const dispatch = createEventDispatcher();

  function toggleMember() {
    if (!previewId) return;
    dispatch('toggle', previewId);
  }

  // Helper function to format stat display
  function formatStat(runtimeValue, baseValue, suffix = '') {
    if (baseValue !== undefined && runtimeValue !== baseValue) {
      const modifier = runtimeValue - baseValue;
      const sign = modifier >= 0 ? '+' : '';
      return `${runtimeValue}${suffix} (${baseValue}${sign}${modifier})`;
    }
    return `${runtimeValue ?? '-'}${suffix}`;
  }

  // Helper to get base stat value
  function getBaseStat(character, statName) {
    return character.stats?.base_stats?.[statName];
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
          <div>
            <span>HP</span>
            <span>
              {#if sel.stats.max_hp != null}
                {(sel.stats.hp ?? 0) + '/' + formatStat(sel.stats.max_hp, getBaseStat(sel, 'max_hp'))}
              {:else}
                {sel.stats.hp ?? '-'}
              {/if}
            </span>
          </div>
          <div><span>EXP</span><span>{sel.stats.exp ?? sel.stats.xp ?? '-'}</span></div>
          <div><span>Vitality</span><span>{formatStat(sel.stats.vitality ?? sel.stats.vita, getBaseStat(sel, 'vitality'))}</span></div>
          <div><span>Regain</span><span>{formatStat(sel.stats.regain ?? sel.stats.regain_rate, getBaseStat(sel, 'regain'))}</span></div>
        {:else if activeTab === 'Offense'}
          <div><span>ATK</span><span>{formatStat(sel.stats.atk, getBaseStat(sel, 'atk'))}</span></div>
          <div><span>CRIT Rate</span><span>{formatStat((sel.stats.critRate ?? sel.stats.crit_rate ?? 0), getBaseStat(sel, 'crit_rate'), '%')}</span></div>
          <div><span>CRIT DMG</span><span>{formatStat((sel.stats.critDamage ?? sel.stats.crit_damage ?? 0), getBaseStat(sel, 'crit_damage'), '%')}</span></div>
          <div><span>Effect Hit Rate</span><span>{formatStat((sel.stats.effectHit ?? sel.stats.effect_hit_rate ?? 0), getBaseStat(sel, 'effect_hit_rate'), '%')}</span></div>
        {:else if activeTab === 'Defense'}
          <div><span>DEF</span><span>{formatStat(sel.stats.defense, getBaseStat(sel, 'defense'))}</span></div>
          <div><span>Mitigation</span><span>{formatStat(sel.stats.mitigation, getBaseStat(sel, 'mitigation'))}</span></div>
          <div><span>Dodge Odds</span><span>{formatStat(sel.stats.dodge_odds, getBaseStat(sel, 'dodge_odds'))}</span></div>
          <div><span>Effect Resist</span><span>{formatStat(sel.stats.effectResist ?? sel.stats.effect_resistance, getBaseStat(sel, 'effect_resistance'))}</span></div>
        {:else if activeTab === 'Effects'}
          {#if sel.stats.active_effects && sel.stats.active_effects.length > 0}
            <div class="effects-header">Active Effects:</div>
            {#each sel.stats.active_effects as effect}
              <div class="effect-item">
                <div class="effect-name">{effect.name}</div>
                <div class="effect-source">Source: {effect.source}</div>
                {#if effect.duration > 0}
                  <div class="effect-duration">Duration: {effect.duration} turns</div>
                {/if}
                <div class="effect-modifiers">
                  {#each Object.entries(effect.modifiers) as [stat, value]}
                    <span class="modifier">{stat}: {value >= 0 ? '+' : ''}{value}</span>
                  {/each}
                </div>
              </div>
            {/each}
          {:else}
            <div class="no-effects">No active effects</div>
          {/if}
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
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.25);
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

/* Effects tab styles */
.effects-header {
  font-weight: bold;
  color: #fff;
  margin-bottom: 0.5rem;
}

.effect-item {
  background: rgba(255,255,255,0.1);
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  border-left: 3px solid #4a9eff;
}

.effect-name {
  font-weight: bold;
  color: #fff;
  margin-bottom: 0.25rem;
}

.effect-source {
  font-size: 0.9rem;
  color: #ccc;
  margin-bottom: 0.25rem;
}

.effect-duration {
  font-size: 0.9rem;
  color: #ffeb3b;
  margin-bottom: 0.5rem;
}

.effect-modifiers {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.modifier {
  background: rgba(0,0,0,0.3);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.modifier:has-text('-') {
  color: #f44336;
  border-color: rgba(244, 67, 54, 0.3);
}

.no-effects {
  color: #888;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}
</style>
