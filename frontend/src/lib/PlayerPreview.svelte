<script>
  /**
   * Shows a portrait preview for the currently selected character.
   *
   * Props:
   * - roster: array of character objects
   * - previewId: ID of character to display
   * - overrideElement: optional element name to use for outline/glow color
   */
  export let roster = [];
  export let previewId;
  export let overrideElement = '';
  import { getElementColor } from './assetLoader.js';
</script>

<div class="preview">
  {#if previewId}
    {#each roster.filter(r => r.id === previewId) as sel}
      {#if sel}
        <img
          src={sel.img}
          alt={sel.name}
          style={`--outline: ${getElementColor(overrideElement || sel.element)};`}
        />
      {/if}
    {/each}
  {:else}
    <div class="placeholder">Select up to 4 allies</div>
  {/if}
</div>

<style>
.preview {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  min-width: 0;
  min-height: 0;
}
.preview img {
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border: 3px solid var(--outline, #555);
  background: #222;
  border-radius: 12px;
  box-shadow:
    0 8px 24px rgba(0,0,0,0.5),
    0 0 18px color-mix(in srgb, var(--outline, #888) 65%, transparent),
    0 0 36px color-mix(in srgb, var(--outline, #888) 35%, transparent);
  display: block;
  margin: 0 auto;
}
.placeholder {
  color: #888;
  font-style: italic;
}
</style>
