<script>
  /*
   * CharacterEditor.svelte
   *
   * Reusable editor for tweaking player or NPC starting stats.
   * - Optional pronouns/damage type fields (for the player)
   * - Percent modifiers for HP, Attack, Defense, Crit Rate, Crit Damage
   *   (total allocation ≤ 100)
   *
   * Modes:
   * - Standalone (default): wrapped in MenuPanel with Save/Close controls.
   * - Embedded (embedded=true): no panel chrome or nav buttons; emits 'change'
   *   on every input so parents can reflect live values (without saving).
   */
  import MenuPanel from './MenuPanel.svelte';
  import { createEventDispatcher } from 'svelte';
  export let pronouns = '';
  export let damageType = 'Light';
  export let hp = 0;
  export let attack = 0;
  export let defense = 0;
  export let critRate = 0;
  export let critDamage = 0;
  // When embedded inside another panel, hide header/actions and outer panel chrome
  export let embedded = false;
  // When false, hide pronouns/damageType fields (for non-player characters)
  export let showIdentity = true;
  export let maxPoints = 100;
  const dispatch = createEventDispatcher();

  $: remaining = maxPoints - hp - attack - defense - critRate - critDamage;

  // Notify parent about any change in embedded mode so it can recompute stats
  function broadcastChange() {
    dispatch('change', {
      pronouns,
      damageType,
      hp: +hp,
      attack: +attack,
      defense: +defense,
      critRate: +critRate,
      critDamage: +critDamage,
    });
  }

  function close() { dispatch('close'); }
  function save() {
    dispatch('save', {
      pronouns,
      damageType,
      hp: +hp,
      attack: +attack,
      defense: +defense,
      critRate: +critRate,
      critDamage: +critDamage,
    });
  }
</script>

{#if !embedded}
<MenuPanel data-testid="character-editor" padding="0.75rem">
  <div class="editor">
    <header class="editor-header">
      <h3>Character Editor</h3>
      <div class="spacer" />
      <button class="mini" on:click={close} title="Close">✕</button>
    </header>
    {#if showIdentity}
      <div class="grid">
        <label for="pronouns">Pronouns</label>
        <input id="pronouns" type="text" maxlength="15" bind:value={pronouns} />
        <label for="damage">Damage Type</label>
        <select id="damage" bind:value={damageType}>
          <option>Light</option>
          <option>Dark</option>
          <option>Wind</option>
          <option>Lightning</option>
          <option>Fire</option>
          <option>Ice</option>
        </select>
      </div>
    {/if}
    <div class="stats">
      <p class="remaining">Points remaining: {remaining}</p>
      <div class="stat-row">
        <label for="hp">HP: {hp}%</label>
        <input id="hp" type="range" min="0" max={hp + remaining} bind:value={hp} />
      </div>
      <div class="stat-row">
        <label for="attack">Attack: {attack}%</label>
        <input id="attack" type="range" min="0" max={attack + remaining} bind:value={attack} />
      </div>
      <div class="stat-row">
        <label for="defense">Defense: {defense}%</label>
        <input id="defense" type="range" min="0" max={defense + remaining} bind:value={defense} />
      </div>
      <div class="stat-row">
        <label for="critRate">Crit Rate: {critRate}%</label>
        <input id="critRate" type="range" min="0" max={critRate + remaining} bind:value={critRate} />
      </div>
      <div class="stat-row">
        <label for="critDamage">Crit Damage: {critDamage}%</label>
        <input id="critDamage" type="range" min="0" max={critDamage + remaining} bind:value={critDamage} />
      </div>
    </div>
    <div class="actions">
      <p class="hint">Note: Changes affect the roster panel immediately and apply to new runs. Ongoing battles won’t update mid-fight.</p>
      <button class="primary" on:click={save}>Save</button>
      <button on:click={close}>Close</button>
    </div>
  </div>
</MenuPanel>
{:else}
<div class="editor editor-embedded" data-testid="character-editor">
  {#if showIdentity}
    <div class="grid">
      <label for="pronouns">Pronouns</label>
      <input id="pronouns" type="text" maxlength="15" bind:value={pronouns} on:input={broadcastChange} />
      <label for="damage">Damage Type</label>
      <select id="damage" bind:value={damageType} on:change={broadcastChange}>
        <option>Light</option>
        <option>Dark</option>
        <option>Wind</option>
        <option>Lightning</option>
        <option>Fire</option>
        <option>Ice</option>
      </select>
    </div>
  {/if}
  <div class="stats">
    <p class="remaining">Points remaining: {remaining}</p>
    <div class="stat-row">
      <label for="hp">HP: {hp}%</label>
      <input id="hp" type="range" min="0" max={hp + remaining} bind:value={hp} on:input={broadcastChange} />
    </div>
    <div class="stat-row">
      <label for="attack">Attack: {attack}%</label>
      <input id="attack" type="range" min="0" max={attack + remaining} bind:value={attack} on:input={broadcastChange} />
    </div>
    <div class="stat-row">
      <label for="defense">Defense: {defense}%</label>
      <input id="defense" type="range" min="0" max={defense + remaining} bind:value={defense} on:input={broadcastChange} />
    </div>
    <div class="stat-row">
      <label for="critRate">Crit Rate: {critRate}%</label>
      <input id="critRate" type="range" min="0" max={critRate + remaining} bind:value={critRate} on:input={broadcastChange} />
    </div>
    <div class="stat-row">
      <label for="critDamage">Crit Damage: {critDamage}%</label>
      <input id="critDamage" type="range" min="0" max={critDamage + remaining} bind:value={critDamage} on:input={broadcastChange} />
    </div>
  </div>
</div>
{/if}

<style>
  .editor { display:flex; flex-direction:column; gap:0.9rem; }
  .editor-header { display:flex; align-items:center; gap:0.5rem; }
  .editor-header h3 { margin:0; font-size:1rem; }
  .spacer { flex:1; }
  .grid { display:grid; grid-template-columns: 120px 1fr; gap:0.4rem 0.6rem; align-items:center; }
  .stats { display:flex; flex-direction:column; gap:0.4rem; }
  .stat-row { display:flex; flex-direction:column; gap:0.2rem; }
  .remaining { margin:0 0 0.2rem 0; font-size:0.85rem; opacity:0.85; }
  .actions { display:flex; justify-content:flex-end; gap:0.5rem; }
  .hint { margin-right: auto; opacity: 0.8; font-size: 0.75rem; }
  button { border:1px solid #fff; background:#0a0a0a; color:#fff; padding:0.35rem 0.8rem; cursor:pointer; font-size:0.8rem; }
  button.primary { background:rgba(120,180,255,0.18); }
  button.primary:hover { background:rgba(120,180,255,0.32); }
  button.mini { padding:0.2rem 0.45rem; font-size:0.7rem; }
  input[type="text"], select { background:#111; border:1px solid #555; color:#fff; padding:0.25rem 0.4rem; font-size:0.8rem; }
  input[type="range"] { width:100%; }
  /* Embedded variant chrome to sit inside stats panel */
  .editor-embedded {
    /* Embedded variant inherits parent panel styling; keep spacing only */
    padding: 0.25rem 0 0 0;
  }
</style>
