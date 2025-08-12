<script>
  import { createEventDispatcher } from 'svelte';
  export let map = [];
  const dispatch = createEventDispatcher();
  function select(room) {
    dispatch('select', room);
  }
</script>

<style>
  ul {
    list-style: none;
    padding: 0;
    display: flex;
    gap: 0.5rem;
  }
  li button {
    border: 2px solid #fff;
    background: transparent;
    color: #fff;
    padding: 0.5rem 1rem;
  }
</style>

<ul>
  {#each map as room}
    <li>
      <button data-testid={`room-${room}`} on:click={() => select(room)}>{room}</button>
    </li>
  {/each}
</ul>
