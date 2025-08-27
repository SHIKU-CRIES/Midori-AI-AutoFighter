<script>
  import { createEventDispatcher } from 'svelte';
  export let message = '';
  export let offset = 0;
  const dispatch = createEventDispatcher();
  function handleEnd() {
    dispatch('done');
  }
</script>

<div class="loot" style={`top: calc(50% - ${offset}px)`} on:animationend={handleEnd}>
  {message}
</div>

<style>
  .loot {
    position: absolute;
    left: 50%;
    transform: translate(-50%, 0);
    color: #fff;
    pointer-events: none;
    animation: rise 1.5s ease-out forwards;
    text-shadow: 0 0 4px #000;
  }
  @keyframes rise {
    from { opacity: 1; transform: translate(-50%, 0); }
    to { opacity: 0; transform: translate(-50%, -40px); }
  }
</style>
