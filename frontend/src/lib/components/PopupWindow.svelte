<script>
  import { createEventDispatcher } from 'svelte';
  import OverlaySurface from './OverlaySurface.svelte';
  import MenuPanel from './MenuPanel.svelte';

  const dispatch = createEventDispatcher();

  export let title = '';
  export let padding = '0.5rem';
  // Constrain popup size (useful for reward overlay)
  export let maxWidth = '820px';
  export let maxHeight = '85vh';
  export let zIndex = 1000;

  function close() {
    dispatch('close');
  }
</script>

<OverlaySurface {zIndex}>
  <div class="box" style={`--max-w: ${maxWidth}; --max-h: ${maxHeight}` }>
  <div class="inner">
  <div class="content-wrap">
  <MenuPanel {padding}>
    {#if title}
      <header class="head">
        <h3>{title}</h3>
        <button class="mini" title="Close" on:click={close}>✕</button>
      </header>
    {/if}
    <slot />
  </MenuPanel>
  </div>
  </div>
  </div>
</OverlaySurface>

<style>
  .head {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .head h3 {
    margin: 0;
    font-size: 1rem;
  }

  .head .mini {
    margin-left: auto;
  }

  .mini {
    border: 1px solid #fff;
    background: #111;
    color: #fff;
    font-size: 0.7rem;
    padding: 0.25rem 0.45rem;
    cursor: pointer;
  }

  .box {
    /* center within overlay */
    margin: auto;
    width: min(var(--max-w), 90%);
    /* Let height shrink to fit content, but cap it */
    max-height: var(--max-h);
    /* Enable vertical scrolling when content exceeds max height */
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    /* allow children to shrink and scroll within */
    min-height: 0;
  }

  .inner {
    /* allow content to size naturally inside the box */
    display: block;
  }

  .content-wrap {
    /* natural content sizing; MenuPanel manages its own overflow */
    display: block;
  }
</style>
