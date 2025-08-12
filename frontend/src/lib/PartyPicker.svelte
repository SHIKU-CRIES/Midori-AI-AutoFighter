<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { getPlayers } from './api.js';

  const dispatch = createEventDispatcher();
  const bgModules = import.meta.glob('./assets/backgrounds/*.png', { as: 'url', eager: true });
  const backgrounds = Object.values(bgModules);
  let background = backgrounds[0];

  const portraitModules = import.meta.glob('./assets/characters/*.png', { as: 'url', eager: true });
  const portraits = portraitModules;

  let roster = [];

  export let selected = [];
  export let showConfirm = false;

  function randomPortrait() {
    const keys = Object.keys(portraits);
    return portraits[keys[Math.floor(Math.random() * keys.length)]];
  }

  onMount(async () => {
    background = backgrounds[Math.floor(Math.random() * backgrounds.length)];
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
  .char-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    border: 2px solid #fff;
    background: rgba(0,0,0,0.6);
    color: #fff;
    padding: 0.25rem 0.5rem;
  }
  .char-btn.selected {
    background: #fff;
    color: #000;
  }
  .char-btn img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }
  button.confirm {
    border: 2px solid #fff;
    background: transparent;
    color: #fff;
    padding: 0.25rem 0.5rem;
    align-self: flex-end;
  }
</style>

<div class="panel" style="background-image: url({background});" data-testid="party-picker">
  <div class="roster" data-testid="roster">
    {#each roster as char}
      <button
        data-testid={`choice-${char.id}`}
        class:char-btn
        class:selected={selected.includes(char.id)}
        on:click={() => toggle(char.id)}>
        <img src={char.img} alt={char.name} />
        <span>{char.name}</span>
      </button>
    {/each}
  </div>
  {#if showConfirm}
    <button class="confirm" data-testid="confirm" on:click={confirm}>Confirm</button>
  {/if}
</div>
