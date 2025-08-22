<script>
  // Simple scrolling list of battle messages.
  export let entries = [];
</script>

<ul class="battle-log">
  {#each entries as line, i}
    <li>{line}</li>
  {/each}
</ul>

<style>
  .battle-log {
    position: absolute;
    bottom: 0.25rem;
    left: 50%;
    transform: translateX(-50%);
    max-height: 8rem;
    overflow-y: auto;
    padding: 0.25rem 0.5rem;
    margin: 0;
    list-style: none;
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
    font-size: 0.65rem;
    z-index: 2;
  }
  .battle-log li { white-space: nowrap; }
</style>
