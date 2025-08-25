<script>
  // Displays HoT and DoT icons for a fighter.
  import { getDotImage, getDotElement, getElementColor } from '../assetLoader.js';

  export let hots = [];
  export let dots = [];
  // layout: 'overlay' positions icons inside the portrait frame.
  // layout: 'bar' renders a horizontal bar (used by the Buff Bar under portraits).
  export let layout = 'overlay';

  function formatTooltip(effect, isHot = false) {
    if (!effect) return '';
    const parts = [effect.name || effect.id];
    if (isHot && effect.healing) parts.push(`Heal: ${effect.healing}`);
    if (!isHot && effect.damage) parts.push(`Dmg: ${effect.damage}`);
    if (effect.turns) parts.push(`Turns: ${effect.turns}`);
    if (effect.source) parts.push(`Src: ${effect.source}`);
    return parts.join(' | ');
  }
</script>

<div class="effects" class:overlay={layout !== 'bar'} class:bar={layout === 'bar'}>
  {#each hots as hot}
    <span class="hot" title={formatTooltip(hot, true)}>
      <img
        class="dot-img"
        src={getDotImage(hot)}
        alt={hot.name || hot.id}
        style={`border-color: ${getElementColor(getDotElement(hot))}`}
      />
      {#if hot.stacks > 1}<span class="stack inside">{hot.stacks}</span>{/if}
    </span>
  {/each}
  {#each dots as dot}
    <span class="dot" title={formatTooltip(dot)}>
      <img
        class="dot-img"
        src={getDotImage(dot)}
        alt={dot.name || dot.id}
        style={`border-color: ${getElementColor(getDotElement(dot))}`}
      />
      {#if dot.stacks > 1}<span class="stack inside">{dot.stacks}</span>{/if}
    </span>
  {/each}
</div>

<style>
  .effects { pointer-events: none; }
  /* Overlay layout: inside portrait frame */
  .effects.overlay {
    position: absolute;
    left: 2px;
    bottom: 2px;
    width: calc(var(--portrait-size) - 4px);
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
    align-items: center;
  }
  /* Bar layout: horizontal row (Buff Bar) */
  .effects.bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
    width: 100%;
    justify-content: center;
  }
  .effects span { position: relative; display: inline-block; }
  .dot-img {
    width: 30px;
    height: 30px;
    border-radius: 4px;
    object-fit: cover;
    display: block;
    border: 2px solid #555;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.25);
  }
  .stack.inside {
    position: absolute;
    bottom: 1px;
    right: 1px;
    font-size: 0.9rem; /* Enlarged DoT/HoT stack numbers */
    font-weight: 800;
    line-height: 1;
    padding: 0 3px;
    border-radius: 2px;
    background: rgba(0,0,0,0.72);
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    pointer-events: none;
  }
</style>
