<script>
  export let padding = '0.5rem';
</script>

<style>
  .panel {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    padding: var(--padding);
    overflow: auto;
    border: 2px solid #777;
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(4px);
  }
</style>

<div class="panel" style={`--padding: ${padding}`}> 
  <slot />
</div>
