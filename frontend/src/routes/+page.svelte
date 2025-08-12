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
    showPicker = true;
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
    { icon: Settings, label: 'Settings' },
    { icon: SquareChartGantt, label: 'Stats' }
  ];

  onMount(() => {
    const update = () => (width = window.innerWidth);
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  });

  $: mode = layoutForWidth(width);
</script>

<style>
  :global(body) {
    background: #000;
    color: #fff;
  }
  .layout { display: grid; min-height: 100vh; gap: 1rem; padding: 1rem; align-items: start; }
  @media (min-width: 1024px) { .layout { grid-template-columns: 3fr 1fr; } }
  @media (min-width: 600px) and (max-width: 1023px) { .layout { grid-template-columns: 1fr; } }
  @media (max-width: 599px) { .layout { grid-template-columns: 1fr; } }

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
  .stack { display: flex; flex-direction: column; gap: 1rem; }
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
</style>

<div class="layout">
  <!-- Left: 16:9 Game Viewport -->
  <GameViewport
    runId={runId}
    roomData={roomData}
    background={viewportBg}
    showPicker={showPicker}
    pickerMode={pickerMode}
    bind:selected={selectedParty}
    on:confirm={startAfterPick}
  />

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

<!-- Global overlay removed; picker now renders inside the 16:9 viewport during Run start -->
