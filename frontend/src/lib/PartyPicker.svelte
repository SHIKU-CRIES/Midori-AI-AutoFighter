<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { getPlayers } from './api.js';
  import { Flame, Snowflake, Zap, Sun, Moon, Wind, Circle } from 'lucide-svelte';

  const dispatch = createEventDispatcher();
  const bgModules = import.meta.glob('./assets/backgrounds/*.png', { eager: true, import: 'default', query: '?url' });
  const backgrounds = Object.values(bgModules);
  let background = backgrounds[0];

  const portraitModules = import.meta.glob('./assets/characters/*.png', { eager: true, import: 'default', query: '?url' });
  const portraits = portraitModules;

  let roster = [];
  let error = '';

  export let selected = [];
  export let showConfirm = false;
  export let compact = false;

  function randomPortrait() {
    const keys = Object.keys(portraits);
    return portraits[keys[Math.floor(Math.random() * keys.length)]];
  }

  onMount(async () => {
    background = backgrounds[Math.floor(Math.random() * backgrounds.length)];
    try {
      const data = await getPlayers();
      roster = data.players
        .map(p => ({
          id: p.id,
          name: p.name,
          img: portraits[`./assets/characters/${p.id}.png`] ?? randomPortrait(),
          owned: p.owned,
          is_player: p.is_player,
          element: p.element ?? 'Generic',
          stats: p.stats ?? { hp: 0, atk: 0, defense: 0, level: 1 }
        }))
        .filter(p => p.owned || p.is_player)
        .sort((a, b) => (a.is_player ? -1 : b.is_player ? 1 : 0));
      const player = roster.find(p => p.is_player);
      if (player) {
        selected = [player.id];
      }
    } catch (e) {
      error = 'Unable to load roster. Is the backend running on 59002?';
    }
  });

  function toggle(id) {
    const char = roster.find(c => c.id === id);
    if (char && char.is_player) {
      return;
    }
    if (selected.includes(id)) {
      selected = selected.filter(c => c !== id);
    } else if (selected.length < 4) {
      selected = [...selected, id];
    }
  }

  function confirm() {
    dispatch('confirm', selected);
  }

  function iconFor(element) {
    const e = (element || '').toLowerCase();
    if (e === 'fire') return Flame;
    if (e === 'ice') return Snowflake;
    if (e === 'lightning') return Zap;
    if (e === 'light') return Sun;
    if (e === 'dark') return Moon;
    if (e === 'wind') return Wind;
    return Circle;
  }
</script>

<style>
  .panel {
    border: 2px solid #fff;
    padding: 1rem;
    background: #000;
    background-size: cover;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: min(90vw, 480px);
    max-height: 80vh;
  }
  /* Fullscreen layout inside game viewport */
  .full {
    display: grid;
    grid-template-columns: 220px 1fr 260px;
    gap: 0.75rem;
    width: min(95%, 1100px);
    height: min(85vh, 95%);
    background: rgba(0,0,0,0.55);
    border: 2px solid #666;
    padding: 0.75rem;
  }
  .panel.compact {
    width: 100%;
    max-width: none;
    background: #0a0a0a;
    background-image: none !important;
    border-color: #555;
    padding: 0.5rem;
    max-height: 200px;
  }
  .roster {
    max-height: 10rem;
    overflow-y: auto;
    mask-image: linear-gradient(to bottom, transparent, black 10%, black 90%, transparent);
    -webkit-mask-image: linear-gradient(to bottom, transparent, black 10%, black 90%, transparent);
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .panel.compact .roster { max-height: 5.5rem; }
  .list { display: flex; flex-direction: column; gap: 0.25rem; }
  .char-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border: 2px solid #fff;
    background: rgba(0,0,0,0.6);
    color: #fff;
    padding: 0.25rem 0.5rem;
    width: 100%;
    justify-content: flex-start;
  }
  .panel.compact .char-btn { border-color: #777; padding: 0.15rem 0.35rem; font-size: 0.85rem; }
  .char-btn.selected {
    background: #fff;
    color: #000;
  }
  .char-btn img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }
  .panel.compact .char-btn img { width: 20px; height: 20px; }
  .elem { width: 16px; height: 16px; opacity: 0.9; }
  .preview { display: flex; align-items: center; justify-content: center; }
  .preview img { max-width: 100%; max-height: 100%; object-fit: contain; border: 2px solid #333; }
  .stats { display: grid; grid-template-columns: auto 1fr; column-gap: 0.5rem; row-gap: 0.25rem; }
  .stats h4 { margin: 0 0 0.5rem 0; grid-column: 1 / -1; font-size: 1rem; color: #ddd; }
  button.confirm {
    border: 2px solid #fff;
    background: transparent;
    color: #fff;
    padding: 0.25rem 0.5rem;
    align-self: flex-end;
  }
</style>

{#if compact}
  <div class="panel compact" data-testid="party-picker">
    <div class="roster list" data-testid="roster">
      {#each roster as char}
        <button
          data-testid={`choice-${char.id}`}
          class="char-btn"
          class:selected={selected.includes(char.id)}
          on:click={() => toggle(char.id)}>
          <img src={char.img} alt={char.name} />
          <span>{char.name}</span>
        </button>
      {/each}
    </div>
  </div>
{:else}
  <div class="full" data-testid="party-picker">
    <!-- Left: Roster with element icons -->
    <div class="roster list">
      {#each roster as char}
        <button
          data-testid={`choice-${char.id}`}
          class="char-btn"
          class:selected={selected.includes(char.id)}
          on:click={() => toggle(char.id)}>
          <svelte:component this={iconFor(char.element)} class="elem" aria-hidden="true" />
          <span>{char.name}</span>
        </button>
      {/each}
    </div>

    <!-- Center: Portrait preview of selected -->
    <div class="preview">
      {#if selected.length}
        {#each roster.filter(r => selected.includes(r.id)).slice(0,1) as sel}
          <img src={sel.img} alt={sel.name} />
        {/each}
      {:else}
        <div class="placeholder">Select up to 4 allies</div>
      {/if}
    </div>

    <!-- Right: Stats of highlighted/first selected -->
    <div class="stats">
      <h4>Stats</h4>
      {#if selected.length}
        {#each roster.filter(r => selected.includes(r.id)).slice(0,1) as sel}
          <span>Element</span><span>{sel.element}</span>
          <span>HP</span><span>{sel.stats.hp}</span>
          <span>ATK</span><span>{sel.stats.atk}</span>
          <span>DEF</span><span>{sel.stats.defense}</span>
          <span>LVL</span><span>{sel.stats.level}</span>
        {/each}
      {:else}
        <span>Element</span><span>-</span>
        <span>HP</span><span>-</span>
        <span>ATK</span><span>-</span>
        <span>DEF</span><span>-</span>
        <span>LVL</span><span>-</span>
      {/if}
      {#if error}
        <small style="color:#f88; grid-column: 1 / -1;">{error}</small>
      {/if}
      {#if showConfirm}
        <div style="grid-column: 1 / -1; display:flex; justify-content:flex-end; margin-top:0.5rem;">
          <button class="confirm" data-testid="confirm" on:click={confirm}>Confirm</button>
        </div>
      {/if}
    </div>
  </div>
{/if}
