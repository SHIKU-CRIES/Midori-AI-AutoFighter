<script>
  export let padding = '0.4rem 0.75rem 0.75rem 0.75rem';
  export let zIndex = 1000;
</script>

<style>
  .surface {
  position: absolute;
  /* use inset to avoid off-by-one issues with borders/padding */
  inset: var(--ui-top-offset) 0 0 0;
  max-width: 100%;
  max-height: calc(100% - var(--ui-top-offset));
  display: flex;
  padding: var(--padding);
  box-sizing: border-box;
  z-index: var(--z, 1000); /* allow callers to control stacking */
  /* allow vertical scrolling; hide stray horizontal scrollbars */
  overflow-x: hidden;
  overflow-y: auto;
  }
</style>

<div class="surface" style={`--padding: ${padding}; --z: ${zIndex}`}>
  <slot />
</div>
