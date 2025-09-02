<script>
  export let padding = '0.4rem 0.75rem 0.75rem 0.75rem';
  export let zIndex = 1000;
  // When true, disable scrolling on the overlay surface itself; let inner content manage scroll
  export let noScroll = false;
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

  .surface.no-scroll {
    overflow-y: hidden;
  }

  /* Themed scrollbars for overlay surface (fallback when panels don't manage scroll) */
  .surface {
    scrollbar-width: thin;
    scrollbar-color: rgba(190, 190, 200, 0.6) rgba(50, 50, 60, 0.35);
  }
  .surface::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  .surface::-webkit-scrollbar-track {
    background: rgba(50, 50, 60, 0.35);
    border-radius: 8px;
  }
  .surface::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(200, 200, 210, 0.55), rgba(160, 160, 175, 0.55));
    border-radius: 8px;
    border: 2px solid rgba(0, 0, 0, 0.2);
  }
  .surface::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, rgba(215, 215, 225, 0.7), rgba(175, 175, 190, 0.7));
  }
</style>

<div class="surface" class:no-scroll={noScroll} style={`--padding: ${padding}; --z: ${zIndex}`}>
  <slot />
</div>
