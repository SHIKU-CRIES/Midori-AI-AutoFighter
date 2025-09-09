<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { crossfade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import jsfxr from 'jsfxr';
  import CurioChoice from './CurioChoice.svelte';
  import { getRewardArt } from '../systems/rewardLoader.js';
  import { getCharacterImage } from '../systems/assetLoader.js';
  import { formatName } from '../systems/craftingUtils.js';

  export let results = [];
  export let reducedMotion = false;

  const dispatch = createEventDispatcher();
  let stack = [];
  let visible = [];
  let isBatch = false;
  let dealSfx;

  const [send, receive] = crossfade({
    duration: () => (reducedMotion ? 0 : 400),
    easing: cubicOut
  });

  function toRenderable(r) {
    if (!r || typeof r !== 'object') return r;
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
        artUrl: getCharacterImage(id)
      };
    }
    if (r.type === 'item') {
      const key = String(r.id || '');
      const stars = Number(r.rarity || 1) || 1;
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
    return r;
  }

  onMount(() => {
    const mapped = Array.isArray(results) ? results.map(toRenderable) : [];
    isBatch = mapped.length === 5 || mapped.length === 10;
    if (isBatch) {
      stack = mapped;
      if (!reducedMotion) {
        try {
          dealSfx = new Audio(jsfxr([0,,0.05,,0.2,,0.1,0.4,,0.3,0.2,,,,,,,,1,,0.5]));
          dealSfx.volume = 0.5;
        } catch {}
      }
      dealNext();
    } else {
      visible = mapped;
    }
  });

  function playDeal() {
    if (reducedMotion || !dealSfx) return;
    try { dealSfx.cloneNode().play(); } catch {}
  }

  function dealNext() {
    if (stack.length === 0) return;
    visible = [...visible, stack.shift()];
    playDeal();
    if (stack.length > 0) {
      setTimeout(dealNext, reducedMotion ? 0 : 400);
    }
  }

  function close() {
    dispatch('close');
  }
</script>

<div class="layout">
  {#if isBatch}
    <div class="stack" aria-hidden={stack.length === 0}>
      {#each stack as r, i (r.id)}
        <div class="card" style={`--i: ${i}`} out:send={{ key: r.id }}>
          <CurioChoice entry={r} disabled={true} />
        </div>
      {/each}
    </div>
  {/if}
  <div class="choices">
    {#each visible as r (r.id)}
      <div class="card" in:receive={{ key: r.id }}>
        <CurioChoice entry={r} disabled={true} />
      </div>
    {/each}
  </div>
  {#if stack.length === 0 && visible.length}
    <button class="done" on:click={close}>Done</button>
  {/if}
</div>

<style>
  .layout {
    position: relative;
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
  .stack {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
  }
  .stack .card {
    position: absolute;
    transform: translate(calc(var(--i) * 4px), calc(var(--i) * 4px));
  }
  .done {
    padding: 0.5rem 1rem;
    background: #0a0a0a;
    color: #fff;
    border: 2px solid #fff;
    cursor: pointer;
  }
</style>
