<script>
  // Pulsing overlay shown while foes are enraged.
  export let active = false;
  export let flashDuration = 10; // seconds
</script>

{#if active}
  <div class="enrage-overlay" style={`--flash-duration: ${flashDuration}s`}></div>
{/if}

<style>
  .enrage-overlay {
    position: absolute;
    inset: 0;
    z-index: 0;
    animation: enrage-bg var(--flash-duration) linear infinite;
  }
  @keyframes enrage-bg {
    0%,100% { background: rgba(0,0,255,0.4); }
    50% { background: rgba(255,0,0,0.4); }
  }
</style>
