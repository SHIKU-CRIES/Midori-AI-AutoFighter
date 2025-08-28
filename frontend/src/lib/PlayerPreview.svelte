<script>
  /**
   * Shows a portrait preview for the currently selected character.
   *
   * Props:
   * - roster: array of character objects
   * - previewId: ID of character to display
   */
  export let roster = [];
  export let previewId;
</script>

<div class="preview">
  {#if previewId}
    {#each roster.filter(r => r.id === previewId) as sel}
      <img src={sel.img} alt={sel.name} />
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
  border: 3px solid #555;
  background: #222;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
  display: block;
  margin: 0 auto;
}
.placeholder {
  color: #888;
  font-style: italic;
}
</style>
