<script>
  /*
   * StatTabs.svelte
   *
   * Renders the character stats panel used by the Party Picker (right column).
   * Features:
   * - Tabbed view (Core, Offense, Defense, Effects).
   * - Shows the currently previewed character's stats and effects.
   * - When the previewed character is the Player, embeds a slim Player Editor
   *   inside the panel (no overlay, no nav buttons) to tweak player starting
   *   percent mods. The editor sends live changes that this component uses to
   *   calculate preview values without saving.
   * - Always shows an "Upgrade Character: Placeholder" note below (all chars)
   *   as a staging area for the future per‑character upgrade UI.
   *
   * Plans:
   * - Wire a real per‑character upgrade flow underneath the placeholder (e.g.,
   *   item consumption, star‑based progression) and display available upgrades.
   * - Provide a compact save/apply control for the embedded player editor, or
   *   auto‑save changes to the backend with clear feedback.
   * - Move editor placement to a fixed sub‑section if we add more widgets.
   */
  import { getElementIcon, getElementColor } from './assetLoader.js';
  import { createEventDispatcher } from 'svelte';
  import PlayerEditor from './PlayerEditor.svelte';
  import { getPlayerConfig } from './api.js';
  import { getPlayerConfig } from './api.js';

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

  // Previewed character and inline editor overlay state
  let previewChar;
  let isPlayer = false;
  let editorVals = null; // { pronouns, damageType, hp, attack, defense }
  let viewStats = {};    // stats object used for display (with overrides when player)
  let loadingEditorCfg = false;

  // Resolve selected entry and whether it's the Player
  $: previewChar = roster.find(r => r.id === previewId);
  $: isPlayer = !!previewChar?.is_player;
  // Lazy‑load the saved Player Editor config when the player is selected.
  $: if (isPlayer && previewChar) {
    if (!editorVals && !loadingEditorCfg) {
      loadingEditorCfg = true;
      (async () => {
        try {
          const cfg = await getPlayerConfig();
          editorVals = {
            pronouns: cfg?.pronouns || '',
            damageType: cfg?.damage_type || 'Light',
            hp: Number(cfg?.hp) || 0,
            attack: Number(cfg?.attack) || 0,
            defense: Number(cfg?.defense) || 0,
          };
        } catch {
          // Fallback to preview runtime stats if config fetch fails
          editorVals = {
            pronouns: previewChar.pronouns || '',
            damageType: previewChar.element || 'Light',
            hp: (previewChar.stats?.max_hp ?? previewChar.stats?.hp ?? 0),
            attack: (previewChar.stats?.atk ?? 0),
            defense: (previewChar.stats?.defense ?? 0),
          };
        } finally {
          loadingEditorCfg = false;
        }
      })();
    }
  } else {
    editorVals = null;
  }
  // Compute displayed stats. For the Player, treat editor values as percent
  // modifiers on base stats (1 point = +1%). Preserve current HP ratio.
  $: {
    const base = previewChar?.stats || {};
    if (isPlayer && editorVals) {
      const baseMax = getBaseStat(previewChar, 'max_hp') ?? base.max_hp ?? 0;
      const baseAtk = getBaseStat(previewChar, 'atk') ?? base.atk ?? 0;
      const baseDef = getBaseStat(previewChar, 'defense') ?? base.defense ?? 0;
      const hpPct = Number(editorVals.hp) || 0;
      const atkPct = Number(editorVals.attack) || 0;
      const defPct = Number(editorVals.defense) || 0;
      const newMax = Math.round(baseMax * (1 + hpPct / 100));
      const hpRatio = baseMax > 0 ? Math.min(1, Math.max(0, (base.hp ?? baseMax) / baseMax)) : 1;
      const newHp = Math.round(newMax * hpRatio);
      const newAtk = Math.round(baseAtk * (1 + atkPct / 100));
      const newDef = Math.round(baseDef * (1 + defPct / 100));
      viewStats = {
        ...base,
        max_hp: newMax,
        hp: newHp,
        atk: newAtk,
        defense: newDef,
      };
    } else {
      viewStats = { ...base };
    }
  }

  function toggleMember() {
    if (!previewId) return;
    dispatch('toggle', previewId);
  }

  // Helper function to format stat display
  // Supports percentage-style values by multiplying by 100 when suffix === '%'.
  function formatStat(runtimeValue, baseValue, suffix = '') {
    const isPercent = suffix === '%';
    const rv = runtimeValue == null ? null : (isPercent ? runtimeValue * 100 : runtimeValue);
    const bv = baseValue == null ? null : (isPercent ? baseValue * 100 : baseValue);

    if (bv !== null && rv !== null && rv !== bv) {
      const modifier = rv - bv;
      const sign = modifier >= 0 ? '+' : '';
      const show = (v) => (Number.isInteger(v) ? v : v.toFixed(1));
      return `${show(rv)}${suffix} (${show(bv)}${sign}${show(modifier)})`;
    }
    if (rv === null) return '-';
    return `${Number.isInteger(rv) ? rv : rv.toFixed(1)}${suffix}`;
  }

  // Helper to format multiplier-style values (e.g., 1.0 -> 1x)
  function formatMult(runtimeValue, baseValue) {
    const rv = runtimeValue == null ? null : Number(runtimeValue);
    const bv = baseValue == null ? null : Number(baseValue);
    const show = (v) => {
      if (v == null || !isFinite(v)) return '-';
      // Prefer integer when close, else show up to 2 decimals
      const rounded = Math.round(v);
      return Math.abs(v - rounded) < 1e-6 ? String(rounded) : v.toFixed(2);
    };
    if (rv === null) return '-';
    if (bv !== null && rv !== bv) {
      const modifier = rv - bv;
      const sign = modifier >= 0 ? '+' : '';
      return `${show(rv)}x (${show(bv)}${sign}${show(modifier)})`;
    }
    return `${show(rv)}x`;
  }

  // Helper to get base stat value (legacy).
  // In current in-run refactor, base comparisons may be unavailable;
  // this returns undefined to suppress base deltas unless provided.
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
              {#if viewStats.max_hp != null}
                {(viewStats.hp ?? 0) + '/' + formatStat(viewStats.max_hp, getBaseStat(sel, 'max_hp'))}
              {:else}
                {viewStats.hp ?? '-'}
              {/if}
            </span>
          </div>
          <div><span>EXP</span><span>{sel.stats.exp ?? sel.stats.xp ?? '-'}</span></div>
          <div><span>Vitality</span><span>{formatMult(sel.stats.vitality ?? sel.stats.vita, getBaseStat(sel, 'vitality'))}</span></div>
          <div><span>Regain</span><span>{formatStat(sel.stats.regain ?? sel.stats.regain_rate, getBaseStat(sel, 'regain'))}</span></div>
        {:else if activeTab === 'Offense'}
          <div><span>ATK</span><span>{formatStat(viewStats.atk, getBaseStat(sel, 'atk'))}</span></div>
          <div><span>CRIT Rate</span><span>{formatStat((sel.stats.critRate ?? sel.stats.crit_rate ?? 0), getBaseStat(sel, 'crit_rate'), '%')}</span></div>
          <div><span>CRIT DMG</span><span>{formatStat((sel.stats.critDamage ?? sel.stats.crit_damage ?? 0), getBaseStat(sel, 'crit_damage'), '%')}</span></div>
          <div><span>Effect Hit Rate</span><span>{formatStat((sel.stats.effectHit ?? sel.stats.effect_hit_rate ?? 0), getBaseStat(sel, 'effect_hit_rate'), '%')}</span></div>
        {:else if activeTab === 'Defense'}
          <div><span>DEF</span><span>{formatStat(viewStats.defense, getBaseStat(sel, 'defense'))}</span></div>
          <div><span>Mitigation</span><span>{formatMult(sel.stats.mitigation, getBaseStat(sel, 'mitigation'))}</span></div>
          <div><span>Dodge Odds</span><span>{formatStat(sel.stats.dodge_odds, getBaseStat(sel, 'dodge_odds'), '%')}</span></div>
          <div><span>Effect Resist</span><span>{formatStat(sel.stats.effectResist ?? sel.stats.effect_resistance, getBaseStat(sel, 'effect_resistance'), '%')}</span></div>
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
                    <span class="modifier" class:negative={value < 0} class:positive={value >= 0}>
                      {stat}: {value >= 0 ? '+' : ''}{value}
                    </span>
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
  {#if previewId}
    {#each roster.filter(r => r.id === previewId) as sel}
      <!--
        Inline editor/upgrade region:
        - Divider separates stats list from interactive controls/notes.
        - Player Editor shows only for the Player (no nav, embedded=true).
        - Upgrade placeholder shows for all characters (future upgrades hub).
      -->
      <div class="hello-anchor">
        <div class="inline-divider" aria-hidden="true"></div>
        {#if sel.is_player}
          <div class="editor-wrap">
            <PlayerEditor
              embedded={true}
              pronouns={editorVals?.pronouns || ''}
              damageType={editorVals?.damageType || 'Light'}
              hp={editorVals?.hp || 0}
              attack={editorVals?.attack || 0}
              defense={editorVals?.defense || 0}
              on:change={(e) => editorVals = e.detail}
            />
          </div>
        {/if}
        <div class="upgrade-placeholder">Upgrade Character: Placeholder</div>
      </div>
    {/each}
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
  position: relative; /* allow absolute positioning for anchored elements */
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

/* Divider and inline half-height spacer below stats within panel */
.inline-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
  margin: 0 0 0.35rem 0;
}
.hello-anchor {
  position: absolute;
  top: 50%;
  left: 1rem;   /* align with stats-panel side padding */
  right: 1rem;  /* align with stats-panel side padding */
}

/* Inline container occupying 50% of the stats panel width */
.editor-wrap { width: 100%; }
.upgrade-placeholder {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #ddd;
}

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

.modifier.negative {
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
