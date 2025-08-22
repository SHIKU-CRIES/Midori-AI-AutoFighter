<script>
  // Displays HoT and DoT icons for a fighter.
  import { getDotImage, getDotElement, getElementColor } from '../assetLoader.js';

  export let hots = [];
  export let dots = [];

  // Collapse duplicate effect names and track stacks.
  function groupEffects(list) {
    const counts = {};
    for (const e of list || []) counts[e] = (counts[e] || 0) + 1;
    return Object.entries(counts);
  }
</script>

<div class="effects">
  {#each groupEffects(hots) as [name]}
    <span class="hot" title={name}>
      <img
        class="dot-img"
        src={getDotImage(name)}
        alt={name}
        style={`border-color: ${getElementColor(getDotElement(name))}`}
      />
      <span class="hot-plus">+</span>
    </span>
  {/each}
  {#each groupEffects(dots) as [name, count]}
    <span class="dot" title={name}>
      <img
        class="dot-img"
        src={getDotImage(name)}
        alt={name}
        style={`border-color: ${getElementColor(getDotElement(name))}`}
      />
      {#if count > 1}<span class="stack inside">{count}</span>{/if}
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
