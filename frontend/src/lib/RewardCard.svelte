<script>
  import CardArt from './CardArt.svelte';
  export let entry = {};
  export let type = 'card';
  export let size = 'normal';
</script>

<button class="card">
  <CardArt {entry} {type} {size} />
</button>

<style>
  .card {
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
  }
</style>
