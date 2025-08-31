<script>
  import { createEventDispatcher, onMount } from 'svelte';

  export let runs = [];
  const dispatch = createEventDispatcher();

  let selected = 0;

  onMount(() => {
    if (!Array.isArray(runs)) runs = [];
    if (runs.length === 0) selected = -1;
  });

  function loadSelected() {
    if (selected < 0 || selected >= runs.length) return;
    const detail = { run: runs[selected] };
    // Emit a custom event name to avoid any browser/DOM 'load' confusion,
    // while preserving the original 'load' event for backward compatibility.
    dispatch('choose', detail);
    dispatch('load', detail);
  }

  function startNew() {
    dispatch('startNew');
  }
</script>

<div class="chooser">
  {#if runs.length > 0}
    <div class="runs">
      {#each runs as r, i}
        <label class="run-item">
          <input type="radio" name="run" bind:group={selected} value={i} />
          <div class="summary">
            <div class="id">{r.run_id}</div>
            <div class="details">
              Floor {r?.map?.floor || 1}, Room {r?.map?.current || 1}, Pressure {r?.map?.rooms?.[0]?.pressure ?? 0}
            </div>
          </div>
        </label>
      {/each}
    </div>
    <div class="actions">
      <button class="icon-btn" on:click={loadSelected} disabled={selected < 0}>Load</button>
      <button class="icon-btn" on:click={startNew}>Start New</button>
    </div>
  {:else}
    <p>No active runs found.</p>
    <div class="actions">
      <button class="icon-btn" on:click={startNew}>Start New</button>
    </div>
  {/if}
  
</div>

<style>
  .chooser { padding: 0.25rem; min-width: 520px; max-width: 90vw; }
  .runs { display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.5rem; }
  .run-item { display: flex; gap: 0.5rem; align-items: center; background: rgba(255,255,255,0.06); padding: 0.35rem 0.5rem; }
  .summary { display: flex; flex-direction: column; gap: 0.15rem; }
  .id { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.8rem; opacity: 0.9; }
  .details { font-size: 0.85rem; opacity: 0.85; }
  .actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.25rem; }
  .icon-btn { background: rgba(255,255,255,0.10); border: none; border-radius: 0; padding: 0.45rem 0.75rem; cursor: pointer; }
  .icon-btn:hover { background: rgba(120,180,255,0.22); }
  .icon-btn:disabled { opacity: 0.5; cursor: default; }
</style>
