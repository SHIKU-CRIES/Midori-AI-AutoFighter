<script>
  import { createEventDispatcher } from 'svelte';
  import RoomView from './RoomView.svelte';
  import PartyPicker from './PartyPicker.svelte';
  export let runId = '';
  export let roomData = null;
  export let background = '';
  export let showPicker = false;
  export let pickerMode = '';
  export let selected = [];

  const dispatch = createEventDispatcher();
  function handleConfirm(e) {
    dispatch('confirm', e.detail);
  }
</script>

<style>
  .viewport-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }
  .viewport {
    aspect-ratio: 16 / 9;
    width: 100%;
    border: 2px solid #fff;
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background-image: var(--bg);
    background-size: cover;
    background-position: center;
  }
  .placeholder {
    color: #ddd;
    font-size: 0.95rem;
    text-align: center;
    backdrop-filter: blur(2px);
    background: rgba(0,0,0,0.35);
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
  }
  .overlay-inset {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
  }
  @media (max-width: 599px) {
    .viewport { aspect-ratio: auto; min-height: 240px; }
  }
</style>

<div class="viewport-wrap">
  <div class="viewport" style={`--bg: url(${background})`}>
    {#if runId && roomData}
      <RoomView result={roomData.result} foes={roomData.foes} party={roomData.party} />
    {:else if runId}
      <div class="placeholder">Select a room on the map to begin</div>
    {:else}
      <div class="placeholder">Click Run to start a new game</div>
    {/if}

    {#if showPicker && pickerMode === 'start'}
      <div class="overlay-inset">
        <PartyPicker bind:selected={selected} showConfirm on:confirm={handleConfirm} />
      </div>
    {/if}
  </div>
  
</div>
