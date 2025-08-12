<script>
  import { onMount } from 'svelte';
  import { Play, Users, Settings, SquareChartGantt } from 'lucide-svelte';
  import PartyPicker from '$lib/PartyPicker.svelte';
  import PlayerEditor from '$lib/PlayerEditor.svelte';
  import StatsPanel from '$lib/StatsPanel.svelte';
  import RunMap from '$lib/RunMap.svelte';
  import { layoutForWidth } from '$lib/layout.js';
  import { startRun, updateParty } from '$lib/api.js';

  let width = 0;
  let runId = '';
  let currentMap = [];
  let selectedParty = ['sample_player'];
  let showPicker = false;

  function handleStart() {
    showPicker = true;
  }

  async function startAfterPick(event) {
    selectedParty = event.detail;
    const data = await startRun();
    runId = data.run_id;
    currentMap = data.map;
    await updateParty(runId, selectedParty);
    showPicker = false;
  }

  const items = [
    { icon: Play, label: 'Run', action: handleStart },
    { icon: Users, label: 'Party' },
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
  .layout {
    display: grid;
    min-height: 100vh;
    background: #000;
    color: #fff;
  }

  @media (min-width: 1024px) {
    .layout {
      grid-template-columns: 1fr 2fr 1fr 1fr;
    }
  }

  @media (min-width: 600px) and (max-width: 1023px) {
    .layout {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 599px) {
    .layout {
      grid-template-columns: 1fr;
    }
  }

  .menu-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    padding: 2rem;
  }

  .cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px solid #fff;
    padding: 1rem;
  }

  .cell svg {
    width: 48px;
    height: 48px;
    stroke-width: 2;
    margin-bottom: 0.5rem;
  }

  .panel {
    border: 2px solid #fff;
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

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
  {#if mode === 'desktop'}
    <PartyPicker bind:selected={selectedParty} />
    <div class="menu-grid">
      {#each items as item}
        <div class="cell" on:click={item.action}>
          <svelte:component this={item.icon} />
          <span>{item.label}</span>
        </div>
      {/each}
    </div>
    <PlayerEditor />
    <StatsPanel />
  {:else if mode === 'tablet'}
    <div class="menu-grid">
      {#each items as item}
        <div class="cell" on:click={item.action}>
          <svelte:component this={item.icon} />
          <span>{item.label}</span>
        </div>
      {/each}
    </div>
    <PartyPicker bind:selected={selectedParty} />
  {:else}
    <div class="menu-grid">
      {#each items as item}
        <div class="cell" on:click={item.action}>
          <svelte:component this={item.icon} />
          <span>{item.label}</span>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if runId}
  <div class="run-info">
    <p data-testid="run-id">Run: {runId}</p>
    <RunMap map={currentMap} />
  </div>
{/if}

{#if showPicker}
  <div class="overlay">
    <PartyPicker showConfirm bind:selected={selectedParty} on:confirm={startAfterPick} />
  </div>
{/if}

