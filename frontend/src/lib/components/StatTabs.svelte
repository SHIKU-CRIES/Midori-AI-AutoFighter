<script>
  /*
   * StatTabs.svelte
   *
   * Renders the character stats panel used by the Party Picker (right column).
   * Features:
   * - Tabbed view (Core, Offense, Defense).
   * - Shows the currently previewed character's stats.
   * - Embeds a slim Character Editor inside the panel for both player and
   *   non‑player characters, allowing percent tweaks to HP, Attack, Defense,
   *   Crit Rate, and Crit Damage. Player changes auto‑save via API.
   * - Renders an `UpgradePanel` beneath the editor so any character can convert
   *   items into upgrade points and spend them on specific stats.
   */
  import { getElementIcon, getElementColor } from '../systems/assetLoader.js';
  import { createEventDispatcher } from 'svelte';
  import CharacterEditor from './CharacterEditor.svelte';
  import UpgradePanel from './UpgradePanel.svelte';
  import { getPlayerConfig, savePlayerConfig } from '../systems/api.js';

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

  // Previewed character and inline editor overlay state
  let previewChar;
  let isPlayer = false;
  let editorVals = null; // { pronouns, damageType, hp, attack, defense, critRate, critDamage }
  let savedEditor = null; // snapshot of saved config to compute deltas
  let viewStats = {};    // stats object used for display (with overrides when player)
  let loadingEditorCfg = false;
  let saveTimer = null;
  function scheduleSave() {
    if (!isPlayer || !editorVals) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(async () => {
      try {
        await savePlayerConfig({
          pronouns: editorVals.pronouns || '',
          damage_type: editorVals.damageType || 'Light',
          hp: Number(editorVals.hp) || 0,
          attack: Number(editorVals.attack) || 0,
          defense: Number(editorVals.defense) || 0,
          crit_rate: Number(editorVals.critRate) || 0,
          crit_damage: Number(editorVals.critDamage) || 0,
        });
      } catch {}
    }, 400);
  }

  // Resolve selected entry and whether it's the Player
  $: previewChar = roster.find(r => r.id === previewId);
  $: isPlayer = !!previewChar?.is_player;
  // Lazy‑load the saved Player Editor config when the player is selected.
  $: if (previewChar) {
    if (isPlayer) {
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
              critRate: Number(cfg?.crit_rate) || 0,
              critDamage: Number(cfg?.crit_damage) || 0,
            };
            savedEditor = { ...editorVals };
            try { dispatch('preview-element', { element: editorVals.damageType }); } catch {}
          } catch {
            // Fallback to preview runtime stats if config fetch fails
            editorVals = {
              pronouns: previewChar.pronouns || '',
              damageType: previewChar.element || 'Light',
              hp: 0,
              attack: 0,
              defense: 0,
              critRate: 0,
              critDamage: 0,
            };
            savedEditor = { pronouns: editorVals.pronouns, damageType: editorVals.damageType, hp: 0, attack: 0, defense: 0, critRate: 0, critDamage: 0 };
            try { dispatch('preview-element', { element: editorVals.damageType }); } catch {}
          } finally {
            loadingEditorCfg = false;
          }
        })();
      }
    } else {
      if (!editorVals || editorVals.pronouns !== (previewChar.pronouns || '')) {
        editorVals = {
          pronouns: previewChar.pronouns || '',
          damageType: previewChar.element || 'Light',
          hp: 0,
          attack: 0,
          defense: 0,
          critRate: 0,
          critDamage: 0,
        };
        savedEditor = { pronouns: editorVals.pronouns, damageType: editorVals.damageType, hp: 0, attack: 0, defense: 0, critRate: 0, critDamage: 0 };
      }
    }
  } else {
    editorVals = null;
  }
  // Compute displayed stats - use backend-computed stats which already include all effects
  $: {
    const statsObj = previewChar?.stats || {};
    const baseStats = statsObj.base_stats || {};
    const result = { ...statsObj };

    // Apply live editor preview changes on top of computed stats
    if (editorVals) {
      const saved = savedEditor || { hp: 0, attack: 0, defense: 0, critRate: 0, critDamage: 0 };
      const hpDelta = (Number(editorVals.hp) || 0) - (Number(saved.hp) || 0);
      const atkDelta = (Number(editorVals.attack) || 0) - (Number(saved.attack) || 0);
      const defDelta = (Number(editorVals.defense) || 0) - (Number(saved.defense) || 0);
      const critRateDelta = (Number(editorVals.critRate) || 0) - (Number(saved.critRate) || 0);
      const critDamageDelta = (Number(editorVals.critDamage) || 0) - (Number(saved.critDamage) || 0);

      // Apply deltas to the already-computed stats (not base stats)
      const currentMax = Number(statsObj.max_hp) || Number(baseStats.max_hp) || 1000;
      const currentAtk = Number(statsObj.atk) || Number(baseStats.atk) || 100;
      const currentDef = Number(statsObj.defense) || Number(baseStats.defense) || 50;
      const currentCritRate = Number(statsObj.crit_rate) || Number(baseStats.crit_rate) || 0.05;
      const currentCritDamage = Number(statsObj.crit_damage) || Number(baseStats.crit_damage) || 2.0;

      result.max_hp = Math.round(currentMax * (1 + hpDelta / 100));
      result.atk = Math.round(currentAtk * (1 + atkDelta / 100));
      result.defense = Math.round(currentDef * (1 + defDelta / 100));
      result.crit_rate = currentCritRate * (1 + critRateDelta / 100);
      result.crit_damage = currentCritDamage * (1 + critDamageDelta / 100);

      // Preserve HP ratio against upgraded max
      const hpRatioBase = Number(statsObj.hp) / Math.max(1, currentMax);
      result.hp = Math.round(result.max_hp * Math.max(0, Math.min(1, isFinite(hpRatioBase) ? hpRatioBase : 1)));
    }

    viewStats = result;
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
          this={getElementIcon((isPlayer && editorVals?.damageType) ? editorVals.damageType : sel.element)}
          class="type-icon"
          style={`color: ${getElementColor((isPlayer && editorVals?.damageType) ? editorVals.damageType : sel.element)}`}
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
          <div><span>CRIT Rate</span><span>{formatStat(viewStats.crit_rate, getBaseStat(sel, 'crit_rate'), '%')}</span></div>
          <div><span>CRIT DMG</span><span>{formatStat(viewStats.crit_damage, getBaseStat(sel, 'crit_damage'), '%')}</span></div>
          <div><span>Effect Hit Rate</span><span>{formatStat(viewStats.effect_hit_rate, getBaseStat(sel, 'effect_hit_rate'), '%')}</span></div>
        {:else if activeTab === 'Defense'}
          <div><span>DEF</span><span>{formatStat(viewStats.defense, getBaseStat(sel, 'defense'))}</span></div>
          <div><span>Mitigation</span><span>{formatMult(viewStats.mitigation, getBaseStat(sel, 'mitigation'))}</span></div>
          <div><span>Dodge Odds</span><span>{formatStat(viewStats.dodge_odds, getBaseStat(sel, 'dodge_odds'), '%')}</span></div>
          <div><span>Effect Resist</span><span>{formatStat(viewStats.effect_resistance, getBaseStat(sel, 'effect_resistance'), '%')}</span></div>
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
      <!-- Inline editor and upgrade region -->
      <div class="hello-anchor">
        <div class="inline-divider" aria-hidden="true"></div>
        <div class="editor-wrap">
          <CharacterEditor
            embedded={true}
            showIdentity={sel.is_player}
            pronouns={editorVals?.pronouns || ''}
            damageType={editorVals?.damageType || 'Light'}
            hp={editorVals?.hp || 0}
            attack={editorVals?.attack || 0}
            defense={editorVals?.defense || 0}
            critRate={editorVals?.critRate || 0}
            critDamage={editorVals?.critDamage || 0}
            on:change={(e) => { editorVals = e.detail; if (sel.is_player) { try { dispatch('preview-element', { element: editorVals.damageType }); } catch {} } scheduleSave(); }}
          />
        </div>
        <UpgradePanel id={sel.id} element={sel.element}
          on:upgraded={() => { try { dispatch('refresh-roster'); } catch {} }}
        />
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
</style>
