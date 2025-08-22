<script>
  import { getElementIcon, getElementColor } from './assetLoader.js';

  /**
   * Displays the available roster and handles character selection.
   *
   * Props:
   * - roster: array of character objects
   * - selected: array of selected character IDs
   * - previewId: ID of the character currently previewed (two-way bound)
   * - compact: render compact icon list when true
   */
  export let roster = [];
  export let selected = [];
  export let previewId;
  export let compact = false;

  function select(id) {
    previewId = id;
  }
</script>

{#if compact}
<div class="roster list compact" data-testid="roster">
  {#each roster.filter(c => selected.includes(c.id)) as char}
    <button
      data-testid={`choice-${char.id}`}
      class="char-btn"
      on:click={() => select(char.id)}>
      <img src={char.img} alt={char.name} class="compact-img" />
    </button>
  {/each}
</div>
{:else}
<div class="roster-list">
  {#each roster as char}
    <button
      type="button"
      data-testid={`choice-${char.id}`}
      class="char-row"
      class:selected={selected.includes(char.id)}
      on:click={() => select(char.id)}
      style={`border-color: ${getElementColor(char.element)}`}> 
      <img src={char.img} alt={char.name} class="row-img" />
      <span class="row-name">{char.name}</span>
      <svelte:component
        this={getElementIcon(char.element)}
        class="row-type"
        style={`color: ${getElementColor(char.element)}`}
        aria-hidden="true" />
    </button>
  {/each}
</div>
{/if}

<style>
.roster-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.4rem;
  height: 100%;
  overflow-y: auto;
  border-right: 2px solid #444;
  border-left: 2px solid #444;
  min-width: 0;
}

.char-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.4rem;
  background: rgba(0,0,0,0.6);
  border: 2px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}
.char-row:hover { background: rgba(20,20,20,0.8); }
.char-row.selected {
  border-color: #ffd700;
  box-shadow: 0 0 8px rgba(255,215,0,0.5);
}
.row-img {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #222;
  flex-shrink: 0;
}
.row-name {
  flex: 1;
  text-align: left;
  color: #fff;
  font-size: 0.9rem;
}
.row-type { width: 20px; height: 20px; flex-shrink: 0; }

/* compact mode */
.roster.list.compact {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem;
  background: transparent;
  border: none;
  min-height: 32px;
  height: auto;
}
.roster.list.compact .char-btn {
  border: none;
  background: transparent;
  padding: 0;
  flex-shrink: 0;
}
.roster.list.compact .char-btn img {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #fff;
}
</style>
