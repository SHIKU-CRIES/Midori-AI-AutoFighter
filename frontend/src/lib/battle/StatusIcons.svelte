<script>
  // Displays HoT and DoT icons for a fighter.
  import { getDotImage, getDotElement, getElementColor } from '../assetLoader.js';

  export let hots = [];
  export let dots = [];

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

<div class="effects">
  {#each hots as hot}
    <span class="hot" title={formatTooltip(hot, true)}>
      <img
        class="dot-img"
        src={getDotImage(hot)}
        alt={hot.name || hot.id}
        style={`border-color: ${getElementColor(getDotElement(hot))}`}
      />
      <span class="hot-plus">+</span>
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
  .effects {
    position: absolute;
    left: 2px;
    bottom: 2px;
    width: calc(var(--portrait-size) - 4px);
    display: flex;
    gap: 0.2rem;
    flex-wrap: wrap;
    align-items: center;
    pointer-events: none;
  }
  .effects span { position: relative; display: inline-block; }
  .hot .hot-plus {
    position: absolute;
    bottom: 2px;
    right: 2px;
    color: #fff;
    font-weight: 800;
    text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    font-size: 0.9rem;
    line-height: 1;
    padding: 0 2px;
    border-radius: 2px;
    background: rgba(0,0,0,0.55);
    pointer-events: none;
  }
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
    bottom: 2px;
    right: 2px;
    font-size: 0.6rem;
    line-height: 1;
    padding: 0 2px;
    border-radius: 2px;
    background: rgba(0,0,0,0.65);
    color: #fff;
    pointer-events: none;
  }
</style>
