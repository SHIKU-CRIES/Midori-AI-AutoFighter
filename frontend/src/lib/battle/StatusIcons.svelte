<script>
  // Displays HoT and DoT icons for a fighter.
  import { getDotImage, getDotElement, getElementColor } from '../assetLoader.js';

  export let hots = [];
  export let dots = [];
  export let active_effects = []; // For special effects like aftertaste, crit boost
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

  function formatEffectTooltip(effect) {
    if (!effect) return '';
    let description = '';
    
    // Special descriptions for known effects
    if (effect.name === 'aftertaste') {
      description = 'Deals a hit with random damage type (10% to 150% damage)';
    } else if (effect.name === 'critical_boost') {
      description = '+0.5% crit rate and +5% crit damage per stack. Removed when taking damage.';
    } else {
      // Generic description from modifiers
      const modParts = [];
      if (effect.modifiers) {
        for (const [stat, value] of Object.entries(effect.modifiers)) {
          const sign = value > 0 ? '+' : '';
          modParts.push(`${stat}: ${sign}${value}`);
        }
      }
      description = modParts.join(', ') || 'Unknown effect';
    }
    
    let tooltip = effect.name || 'Unknown Effect';
    if (description) tooltip += `: ${description}`;
    if (effect.duration > 0) tooltip += ` (${effect.duration} turns)`;
    return tooltip;
  }
  // internal state for bar layout paging
  let startIndex = 0;
  const pageSize = 3;
  $: effects = [
    ...(Array.isArray(hots) ? hots.map((e) => ({ type: 'hot', data: e })) : []),
    ...(Array.isArray(dots) ? dots.map((e) => ({ type: 'dot', data: e })) : [])
  ];
  $: total = effects.length;
  $: showArrows = layout === 'bar' && total > pageSize;
  $: visible = layout === 'bar' ? effects.slice(startIndex, Math.min(total, startIndex + pageSize)) : [];
  function next() { if (startIndex + pageSize < total) startIndex += 1; }
  function prev() { if (startIndex > 0) startIndex -= 1; }
  $: if (startIndex + pageSize > total) startIndex = Math.max(0, total - pageSize);
</script>

<div class="effects" class:overlay={layout !== 'bar'} class:bar={layout === 'bar'}>
  {#if layout === 'bar'}
    {#if showArrows}
      <button class="nav left" on:click={prev} disabled={startIndex === 0} aria-label="Previous buffs">‹</button>
    {/if}
    <div class="icons">
      {#each visible as eff}
        <span class={eff.type} title={formatTooltip(eff.data, eff.type === 'hot')}>
          <img
            class="dot-img"
            src={getDotImage(eff.data)}
            alt={eff.data.name || eff.data.id}
            style={`border-color: ${getElementColor(getDotElement(eff.data))}`}
          />
          {#if eff.data.stacks > 1}<span class="stack inside">{eff.data.stacks}</span>{/if}
        </span>
      {/each}
    </div>
    {#if showArrows}
      <button class="nav right" on:click={next} disabled={startIndex + pageSize >= total} aria-label="Next buffs">›</button>
    {/if}
  {:else}
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
    <!-- Special Effects (aftertaste, crit boost, etc.) -->
    {#each (active_effects || []) as effect}
      <span class="special-effect" title={formatEffectTooltip(effect)}>
        {effect.name}
      </span>
    {/each}
  {/if}
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
    align-items: center;
    width: 100%;
    justify-content: center;
    gap: 0.25rem;
    pointer-events: auto; /* allow nav buttons to be clicked */
  }
  .effects.bar .icons {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .effects.bar .nav {
    all: unset;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.25rem;
    height: 1.25rem;
    line-height: 1;
    border-radius: 2px;
    background: rgba(0,0,0,0.35);
    color: #fff;
    cursor: pointer;
    user-select: none;
  }
  .effects.bar .nav:disabled {
    opacity: 0.35;
    cursor: default;
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
  
  /* Special Effects styling */
  .special-effect {
    display: inline-block;
    padding: 2px 6px;
    background: rgba(0, 100, 255, 0.8);
    color: white;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: 600;
    text-shadow: 0 1px 1px rgba(0,0,0,0.6);
    border: 1px solid rgba(0, 150, 255, 0.9);
    cursor: help;
  }
</style>
