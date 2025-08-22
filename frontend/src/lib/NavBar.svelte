<!--
  NavBar.svelte
  Displays top-left navigation controls and snapshot status.
  Emits high-level navigation events without managing run logic.
-->
<script>
  import { Diamond, User, Settings, Swords, ArrowLeft } from 'lucide-svelte';
  import { createEventDispatcher } from 'svelte';

  export let battleActive = false;
  export let viewMode = 'main';
  export let snapshotLoading = false;
  const dispatch = createEventDispatcher();
</script>

<div class="nav-wrapper">
  <div class="stained-glass-bar">
    {#if battleActive}
      <button class="icon-btn" title="Battle">
        <Swords size={22} color="#fff" />
      </button>
    {:else}
      <button class="icon-btn" title="Home" on:click={() => dispatch('home')}>
        <Diamond size={22} color="#fff" />
      </button>
    {/if}
    <button class="icon-btn" title="Player Editor" on:click={() => dispatch('openEditor')}>
      <User size={22} color="#fff" />
    </button>
    <button class="icon-btn" title="Settings" on:click={() => dispatch('settings')}>
      <Settings size={22} color="#fff" />
    </button>
    {#if viewMode !== 'main'}
      <button class="icon-btn" title="Back" on:click={() => dispatch('back')}>
        <ArrowLeft size={22} color="#fff" />
      </button>
    {/if}
  </div>
  <div class="snapshot-panel" class:active={snapshotLoading}>
    <div class="spinner"></div>
    <span>Syncing...</span>
  </div>
</div>

<style>
  .nav-wrapper { position: absolute; top: 1.2rem; left: 1.2rem; display: flex; gap: 0.5rem; z-index: 10; }
  .stained-glass-bar { display: flex; gap: 0.5rem; padding: 0.5rem 0.7rem; border-radius: 0; background: var(--glass-bg); box-shadow: var(--glass-shadow); border: var(--glass-border); backdrop-filter: var(--glass-filter); opacity: 0.99; }
  .icon-btn { background: rgba(255,255,255,0.10); border: none; border-radius: 0; width: 2.9rem; height: 2.9rem; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.18s, box-shadow 0.18s; box-shadow: 0 1px 4px 0 rgba(0,40,120,0.10); }
  .icon-btn:hover { background: rgba(120,180,255,0.22); box-shadow: 0 2px 8px 0 rgba(0,40,120,0.18); }
  .icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .snapshot-panel { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.7rem; border-radius: 0; background: var(--glass-bg); box-shadow: var(--glass-shadow); border: var(--glass-border); backdrop-filter: var(--glass-filter); opacity: 0; transition: opacity 0.2s; }
  .snapshot-panel.active { opacity: 0.99; }
  .spinner { width: 1rem; height: 1rem; border: 2px solid #fff; border-right-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
