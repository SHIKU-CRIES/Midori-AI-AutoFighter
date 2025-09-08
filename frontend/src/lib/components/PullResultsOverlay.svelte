<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import CurioChoice from './CurioChoice.svelte';
  import { getRewardArt } from '../systems/rewardLoader.js';
  import { getCharacterImage } from '../systems/assetLoader.js';
  import { formatName } from '../systems/craftingUtils.js';

  export let results = [];

  const dispatch = createEventDispatcher();
  let queue = [];
  let visible = [];

  function toRenderable(r) {
    if (!r || typeof r !== 'object') return r;
    // Backend provides: { type: 'character'|'item', id, rarity, stacks? }
    if (r.type === 'character') {
      const id = String(r.id || '');
      const stars = Number(r.rarity || 5) || 5;
      const stacks = Number(r.stacks || 0) || 0;
      const about = stacks > 1 ? `Duplicate +${stacks - 1}` : 'New character';
      return {
        id,
        name: id,
        stars,
        about,
        // Use character portrait for the glyph image, keep relic-style frame
        artUrl: getCharacterImage(id)
      };
    }
    if (r.type === 'item') {
      const key = String(r.id || ''); // e.g., 'fire_3'
      const stars = Number(r.rarity || 1) || 1;
      // Normalize for itemArt keys: 'fire_3' -> 'fire3'
      const normalized = key.replace('_', '');
      const artUrl = getRewardArt('item', normalized);
      return {
        id: key,
        name: formatName(key),
        stars,
        about: 'Upgrade material',
        artUrl
      };
    }
    // Fallback: pass through unchanged
    return r;
  }

  onMount(() => {
    queue = Array.isArray(results) ? results.map(toRenderable) : [];
    showNext();
  });

  function showNext() {
    if (queue.length === 0) return;
    visible = [...visible, queue.shift()];
    if (queue.length > 0) {
      setTimeout(showNext, 400);
    }
  }

  function close() {
    dispatch('close');
  }
</script>

<div class="layout">
  <div class="choices">
    {#each visible as r, i (i)}
      <div class="reveal" style={`--delay: ${i * 120}ms`}>
        <CurioChoice entry={r} disabled={true} />
      </div>
    {/each}
  </div>
  {#if queue.length === 0 && visible.length}
    <button class="done" on:click={close}>Done</button>
  {/if}
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
  .choices {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: center;
  }
  .done {
    padding: 0.5rem 1rem;
    background: #0a0a0a;
    color: #fff;
    border: 2px solid #fff;
    cursor: pointer;
  }
  .reveal {
    opacity: 0;
    animation: overlay-reveal 0.4s forwards;
  }
  @keyframes overlay-reveal {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
</style>
