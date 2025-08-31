<script>
  import { onMount } from 'svelte';
  import { getUpgrade, upgradeCharacter } from './systems/api.js';

  export let id;
  export let element;

  let level = 0;
  let items = {};
  let loading = true;

  async function load() {
    loading = true;
    try {
      const data = await getUpgrade(id);
      level = data.level || 0;
      items = data.items || {};
    } finally {
      loading = false;
    }
  }

  onMount(load);

  $: key1 = `${element}_1`;
  $: key2 = `${element}_2`;
  $: key3 = `${element}_3`;
  $: key4 = `${element}_4`;
  $: have1 = items[key1] || 0;
  $: have2 = items[key2] || 0;
  $: have3 = items[key3] || 0;
  $: have4 = items[key4] || 0;
  $: canUpgrade =
    have4 >= 20 || have3 >= 100 || have2 >= 500 || have1 >= 1000;

  async function doUpgrade() {
    await upgradeCharacter(id);
    await load();
  }
</script>

<div class="upgrade-panel" data-testid="upgrade-panel">
  {#if loading}
    <div>Loading upgrades...</div>
  {:else}
    <div>Upgrade Level: {level}</div>
    <div>
      Items: 1★ {have1}, 2★ {have2}, 3★ {have3}, 4★ {have4}
    </div>
    <div class="cost">Cost: 20×4★ or 100×3★ or 500×2★ or 1000×1★</div>
    <button on:click={doUpgrade} disabled={!canUpgrade}>Upgrade</button>
  {/if}
</div>

<style>
.upgrade-panel {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #ddd;
}
.upgrade-panel button {
  margin-top: 0.25rem;
}
.upgrade-panel .cost {
  margin-top: 0.25rem;
  font-size: 0.8rem;
}
</style>
