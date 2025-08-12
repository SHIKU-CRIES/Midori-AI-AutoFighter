<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { getPlayers } from './api.js';

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
          is_player: p.is_player
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
  button.confirm {
    border: 2px solid #fff;
    background: transparent;
    color: #fff;
    padding: 0.25rem 0.5rem;
    align-self: flex-end;
  }
</style>

<div class="panel" class:compact={compact} style="background-image: url({background});" data-testid="party-picker">
  {#if !compact}
    <h3>Pick your party</h3>
    <small>Choose up to 4 allies</small>
  {/if}
  <div class="roster" data-testid="roster">
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
  {#if error}
    <small style="color:#f88">{error}</small>
  {/if}
  {#if showConfirm}
    <button class="confirm" data-testid="confirm" on:click={confirm}>Confirm</button>
  {/if}
</div>
