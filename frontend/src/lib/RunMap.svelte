<script>
  import { createEventDispatcher } from 'svelte';
  export let map = [];
  const dispatch = createEventDispatcher();
  function select(room) {
    dispatch('select', room);
  }
</script>

<style>
  .panel { border: 2px solid #fff; padding: 0.5rem; }
  ul {
    list-style: none;
    padding: 0;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  li button {
    border: 2px solid #fff;
    background: #111;
    color: #fff;
    padding: 0.5rem 1rem;
    min-width: 90px;
  }
  h4 { margin: 0 0 0.5rem 0; }
  .help { color: #ccc; font-size: 0.8rem; }
  .wrap { width: min(100%, 640px); }
  .wrap.small { width: min(100%, 320px); }
  @media (max-width: 599px) {
    .wrap { width: 100%; }
  }
  </style>

<div class="panel wrap" data-testid="run-map">
  <h4>Map</h4>
  <div class="help">Tap a room to proceed</div>
  <ul>
    {#each map as room}
      <li>
        <button data-testid={`room-${room}`} on:click={() => select(room)}>{room}</button>
      </li>
    {/each}
  </ul>
</div>
