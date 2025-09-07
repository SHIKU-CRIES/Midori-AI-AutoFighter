<script>
  export let items = [];
</script>

<div class="stained-glass-side">
  {#each items as item}
    <button class="icon-btn" title={item.label} on:click={item.action} disabled={item.disabled}>
      <div class="btn-content">
        {#if item.icon}
          <div class="icon">
            <svelte:component this={item.icon} size={24} color="#fff" />
          </div>
          <span class="label">{item.label}</span>
        {:else}
          <span class="label">{item.label}</span>
        {/if}
      </div>
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
    min-width: 140px;
  }
  .icon-btn {
    background: rgba(255,255,255,0.10);
    border: none;
    border-radius: 0;
    width: 100%;
    min-height: 3.2rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    cursor: pointer;
    transition: background 0.18s, box-shadow 0.18s;
    box-shadow: 0 1px 4px 0 rgba(0,40,120,0.10);
    padding: 0.4rem 0.6rem;
  }
  .btn-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
  }
  .icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .label {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    white-space: nowrap;
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
