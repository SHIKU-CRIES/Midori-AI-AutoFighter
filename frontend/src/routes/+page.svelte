<script>
  import { onMount } from 'svelte';
  import { Play, Users, Settings, SquareChartGantt } from 'lucide-svelte';
  import PartyPicker from '$lib/PartyPicker.svelte';
  import RunMap from '$lib/RunMap.svelte';
  import GameViewport from '$lib/GameViewport.svelte';
  import { layoutForWidth } from '$lib/layout.js';
  import {
    startRun,
    updateParty,
    battleRoom,
    shopRoom,
    restRoom
  } from '$lib/api.js';

  let width = 0;
  let runId = '';
  let currentMap = [];
  let selectedParty = ['sample_player'];
  let roomData = null;
  let showPicker = false;
  let pickerMode = '';
  let viewportBg = '';

  function handleStart() {
    pickerMode = 'start';
    showPicker = true;
  }

  function handleParty() {
    pickerMode = 'party';
    showPicker = false;
  }

  async function startAfterPick(event) {
    selectedParty = event.detail;
    if (pickerMode === 'start') {
      const data = await startRun();
      runId = data.run_id;
      currentMap = data.map;
      await updateParty(runId, selectedParty);
    }
    showPicker = false;
  }

  async function handleRoom(room) {
    if (!runId) return;
    if (room === 'battle') {
      roomData = await battleRoom(runId);
    } else if (room === 'shop') {
      roomData = await shopRoom(runId);
    } else if (room === 'rest') {
      roomData = await restRoom(runId);
    }
  }

  const items = [
    { icon: Play, label: 'Run', action: handleStart },
    { icon: Users, label: 'Party', action: handleParty },
    { icon: Settings, label: 'Settings', action: handleSettings },
    { icon: SquareChartGantt, label: 'Stats' }
  ];
  // Settings controls
  let showSettings = false;
  let soundVol = 50;
  let musicVol = 50;
  let voiceVol = 50;

  function handleSettings() {
    showSettings = true;
  }
  function confirmSettings() {
    // TODO: apply volume settings via API or state
    showSettings = false;
  }
  function cancelSettings() {
    showSettings = false;
  }

  onMount(() => {
    const update = () => (width = window.innerWidth);
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  });

  $: mode = layoutForWidth(width);
</script>

<style>
  /* constrain page height and hide overflow */
  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
    background: #000;
    color: #fff;
  }
  /* layout as flex column to structure viewport and panels */
  .layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1rem;
    gap: 1rem;
  }

  .menu-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
    padding: 0.5rem;
  }

  .cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px solid #fff;
    padding: 1rem;
    background: #111;
    color: #fff;
    cursor: pointer;
  }

  .cell svg {
    width: 48px;
    height: 48px;
    stroke-width: 2;
    margin-bottom: 0.5rem;
  }

  .panel { border: 2px solid #fff; padding: 0.75rem; background: #0a0a0a; }
  /* Panels grow and scroll if needed */
  .stack {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow-y: auto;
  }
  @media (min-width: 1024px) {
    .stack { flex-direction: row; }
    .stack > section { flex: 1; }
  }
  .section h3 { margin: 0 0 0.5rem 0; font-size: 1rem; color: #ddd; }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Fixed GameViewport height */
  .viewport-wrap {
    flex: none;
    height: 60vh;
    overflow: hidden;
    border: 2px solid #fff;
  }
</style>

<div class="layout">
  <!-- Left: 16:9 Game Viewport -->
  <div class="viewport-wrap">
    <GameViewport
      runId={runId}
      roomData={roomData}
      background={viewportBg}
      showPicker={showPicker}
      pickerMode={pickerMode}
      bind:selected={selectedParty}
      on:confirm={startAfterPick}
    />
  </div>

  <!-- Right: Stacked panels on desktop; full-width on tablet/phone -->
  <div class="stack">
    <section class="panel section">
      <h3>Menu</h3>
      <div class="menu-grid">
        {#each items as item}
          <button type="button" class="cell" on:click={item.action}>
            <svelte:component this={item.icon} />
            <span>{item.label}</span>
          </button>
        {/each}
      </div>
    </section>

    <section class="panel section">
      <h3>Party</h3>
  <PartyPicker compact bind:selected={selectedParty} />
    </section>

    <!-- Player Editor and Stats hidden for now to simplify layout -->
  </div>
</div>

{#if runId}
  <div class="panel section" style="margin: 1rem;">
    <h3>Run</h3>
    <p data-testid="run-id" style="margin:0 0 0.5rem 0;">Run: {runId}</p>
    <RunMap map={currentMap} on:select={(e) => handleRoom(e.detail)} />
  </div>
{/if}

<!-- Settings Panel -->
{#if showSettings}
  <div class="overlay">
    <div class="panel section" style="width: 90%; max-width: 400px;">
      <h3>Settings</h3>
      <div>
        <label>Sound Volume: {soundVol}%</label>
        <input type="range" min="0" max="100" bind:value={soundVol} />
      </div>
      <div>
        <label>Music Volume: {musicVol}%</label>
        <input type="range" min="0" max="100" bind:value={musicVol} />
      </div>
      <div>
        <label>Voice Volume: {voiceVol}%</label>
        <input type="range" min="0" max="100" bind:value={voiceVol} />
      </div>
      <div class="stats-confirm" style="margin-top:1rem; display:flex; justify-content:flex-end; gap:0.5rem;">
        <button class="cell" on:click={cancelSettings}>Cancel</button>
        <button class="cell" on:click={confirmSettings}>Confirm</button>
      </div>
    </div>
  </div>
{/if}
