<script>
  import CardArt from './CardArt.svelte';
  export let entry = {};
  export let size = 'normal';
</script>

<button class="curio">
  <CardArt {entry} type="relic" roundIcon={true} {size} />
</button>

<style>
  .curio {
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
  }
</style>
