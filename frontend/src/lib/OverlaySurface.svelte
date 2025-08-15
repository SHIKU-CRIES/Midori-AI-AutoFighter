<script>
  export let padding = '0.4rem 0.75rem 0.75rem 0.75rem';
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
  z-index: 5;
  /* allow overlay content to scroll instead of being clipped */
  overflow: auto;
  }
</style>

<div class="surface" style={`--padding: ${padding}`}>
  <slot />
</div>
