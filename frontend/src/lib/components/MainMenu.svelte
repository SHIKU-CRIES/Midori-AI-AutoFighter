<script>
  export let items = [];
</script>

<div class="stained-glass-side">
  {#each items as item}
    <button class="icon-btn" title={item.label} on:click={item.action} disabled={item.disabled}>
      {#if item.icon}
        <svelte:component this={item.icon} size={20} color="#fff" />
      {:else}
        <span>{item.label}</span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .stained-glass-side {
    position: absolute;
    top: calc(var(--ui-top-offset) + 1.2rem);
    right: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding: 0.6rem 0.5rem;
    border-radius: 0;
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    z-index: 10;
    backdrop-filter: var(--glass-filter);
    max-height: calc(100% - var(--ui-top-offset) - 2.4rem);
    overflow: auto;
    align-items: center;
  }
  .icon-btn {
    background: rgba(255,255,255,0.10);
    border: none;
    border-radius: 0;
    width: 3.2rem;
    height: 3.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.18s, box-shadow 0.18s;
    box-shadow: 0 1px 4px 0 rgba(0,40,120,0.10);
  }
  .icon-btn:hover {
    background: rgba(120,180,255,0.22);
  }
  .icon-btn:active {
    background: rgba(80,140,220,0.28);
  }
  .icon-btn:disabled {
    opacity: 0.5;
    cursor: default;
  }
</style>
