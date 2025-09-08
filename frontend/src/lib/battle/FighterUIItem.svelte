<script>
  import { Circle as PipCircle } from 'lucide-svelte';
  import Spinner from '../components/Spinner.svelte';
  import { getCharacterImage, getElementColor } from '../systems/assetLoader.js';

  export let fighter = {};
  export let position = 'bottom'; // 'top' for foes, 'bottom' for party
  export let reducedMotion = false;
  export let size = 'normal'; // 'normal' or 'small'
  export let sizePx = 0; // optional explicit pixel size override

  $: elColor = getElementColor(fighter.element);
  // Make party (bottom) portraits larger for readability
  $: portraitSize = sizePx ? `${sizePx}px` : (size === 'small' ? '48px' : (position === 'bottom' ? '256px' : '96px'));
  
  // Element-specific glow effects for different damage types
  $: elementGlow = getElementGlow(fighter.element);

  // Old action pips display removed; no numeric/pip actions overlay.

  function getStackCount(p) {
    const stacks = p?.stacks;
    if (typeof stacks === 'object') {
      if ('count' in stacks) return stacks.count;
      return stacks.mitigation ?? 0;
    }
    return stacks ?? 0;
  }
  
  function getElementGlow(element) {
    switch(element?.toLowerCase()) {
      case 'fire':
        return {
          color: '#ff4444',
          effect: 'fire-glow',
          animation: 'fire-flicker'
        };
      case 'water':
      case 'ice':
        return {
          color: '#4444ff',
          effect: 'water-glow',
          animation: 'water-ripple'
        };
      case 'earth':
      case 'ground':
        return {
          color: '#8b4513',
          effect: 'earth-glow',
          animation: 'earth-pulse'
        };
      case 'air':
      case 'wind':
      case 'lightning':
        return {
          color: '#ffff44',
          effect: 'air-glow',
          animation: 'air-spark'
        };
      case 'light':
      case 'holy':
        return {
          color: '#ffffaa',
          effect: 'light-glow',
          animation: 'light-shine'
        };
      case 'dark':
      case 'shadow':
        return {
          color: '#6644aa',
          effect: 'dark-glow',
          animation: 'dark-pulse'
        };
      default:
        return {
          color: '#888888',
          effect: 'generic-glow',
          animation: 'generic-pulse'
        };
    }
  }

  $: isDead = (fighter?.hp || 0) <= 0;
</script>

<div 
  class="modern-fighter-card {position} {size}"
  class:dead={isDead}
  style="--portrait-size: {portraitSize}; --element-color: {elColor}; --element-glow-color: {elementGlow.color}"
>
  <div class="fighter-portrait">
      <div 
        class="portrait-image"
        class:element-glow={!reducedMotion && !isDead && Boolean(fighter?.ultimate_ready)}
        style="background-image: url({getCharacterImage(fighter?.id || fighter?.summon_type || '')})"
      >
      {#if !reducedMotion && !isDead && fighter?.ultimate_ready}
        <div class="element-effect {elementGlow.effect}"></div>
      {/if}
    </div>
    <!-- Overlay UI: pips (left), passives (middle), ult gauge (right) -->
    <div class="overlay-ui">
      <!-- Old "action pips" removed to avoid confusion with passive pips. -->
      {#if (fighter.passives || []).length}
        <div class="passive-indicators" class:reduced={reducedMotion}>
          {#each fighter.passives as p (p.id)}
            {@const count = getStackCount(p)}
            <div class="passive" class:pips-mode={(p.display === 'pips' && count <= 5)} class:spinner-mode={(p.display === 'spinner')} class:number-mode={(p.display !== 'spinner' && !(p.display === 'pips' && count <= 5))}>
              {#if p.display === 'spinner'}
                <Spinner style="color: var(--element-color)" size="1.2rem" thickness="3px" />
              {:else if p.display === 'pips'}
                {#if count <= 5}
                  <div class="pips">
                    {#each Array(count) as _, i (i)}
                      <PipCircle
                        class="pip-icon filled"
                        stroke="none"
                        fill="currentColor"
                        aria-hidden="true"
                      />
                    {/each}
                  </div>
                {:else}
                  <span class="count">{count}</span>
                {/if}
              {:else}
                <span class="count">{p.max_stacks ? `${count}/${p.max_stacks}` : count}</span>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
      <div
        class="ult-gauge"
        class:ult-ready={Boolean(fighter?.ultimate_ready)}
        style="--element-color: {elColor}; --p: {Math.max(0, Math.min(1, Number(fighter?.ultimate_charge || 0) / 15))}"
        aria-label="Ultimate Gauge"
      >
        <div class="ult-fill"></div>
        {#if !fighter?.ultimate_ready}
          <div class="ult-pulse" style={`animation-duration: ${Math.max(0.4, 1.6 - 1.2 * Math.max(0, Math.min(1, Number(fighter?.ultimate_charge || 0) / 15)))}s`}></div>
        {/if}
        {#if fighter?.ultimate_ready}
          <div class="ult-glow"></div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .modern-fighter-card {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .fighter-portrait {
    position: relative;
    width: var(--portrait-size);
    height: var(--portrait-size);
    border-radius: 8px;
    overflow: hidden;
    background: var(--glass-bg);
    border: 2px solid var(--element-color, rgba(255, 255, 255, 0.3));
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }

  .portrait-image {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    position: relative;
    transition: all 0.3s ease;
  }

  .element-effect {
    position: absolute;
    inset: 0;
    pointer-events: none;
    opacity: 0.6;
  }

  /* Element-specific visual effects */
  .fire-glow {
    background: radial-gradient(circle at 50% 80%, 
      rgba(255, 68, 68, 0.3) 0%,
      rgba(255, 140, 0, 0.2) 40%,
      transparent 70%);
    animation: fire-flicker 2s ease-in-out infinite alternate;
  }

  .water-glow {
    background: radial-gradient(circle at 50% 50%, 
      rgba(68, 68, 255, 0.3) 0%,
      rgba(100, 200, 255, 0.2) 40%,
      transparent 70%);
    animation: water-ripple 3s ease-in-out infinite;
  }

  .earth-glow {
    background: radial-gradient(circle at 50% 100%, 
      rgba(139, 69, 19, 0.3) 0%,
      rgba(160, 82, 45, 0.2) 40%,
      transparent 70%);
    animation: earth-pulse 4s ease-in-out infinite;
  }

  .air-glow {
    background: radial-gradient(circle at 50% 20%, 
      rgba(255, 255, 68, 0.3) 0%,
      rgba(255, 255, 200, 0.2) 40%,
      transparent 70%);
    animation: air-spark 1.5s ease-in-out infinite;
  }

  .light-glow {
    background: radial-gradient(circle at 50% 50%, 
      rgba(255, 255, 170, 0.4) 0%,
      rgba(255, 255, 255, 0.2) 40%,
      transparent 70%);
    animation: light-shine 3s ease-in-out infinite;
  }

  .dark-glow {
    background: radial-gradient(circle at 50% 50%, 
      rgba(102, 68, 170, 0.4) 0%,
      rgba(75, 0, 130, 0.3) 40%,
      transparent 70%);
    animation: dark-pulse 2.5s ease-in-out infinite;
  }

  .generic-glow {
    background: radial-gradient(circle at 50% 50%, 
      rgba(136, 136, 136, 0.2) 0%,
      transparent 60%);
    animation: generic-pulse 3s ease-in-out infinite;
  }

  /* Element animations */
  @keyframes fire-flicker {
    0%, 100% { 
      opacity: 0.4;
      transform: scale(1);
    }
    50% { 
      opacity: 0.7;
      transform: scale(1.05);
    }
  }

  @keyframes water-ripple {
    0%, 100% { 
      opacity: 0.3;
      transform: scale(1) rotate(0deg);
    }
    33% { 
      opacity: 0.5;
      transform: scale(1.02) rotate(1deg);
    }
    66% { 
      opacity: 0.4;
      transform: scale(0.98) rotate(-1deg);
    }
  }

  @keyframes earth-pulse {
    0%, 100% { 
      opacity: 0.2;
      transform: scale(1);
    }
    50% { 
      opacity: 0.4;
      transform: scale(1.03);
    }
  }

  @keyframes air-spark {
    0%, 100% { 
      opacity: 0.3;
      filter: brightness(1);
    }
    25% { 
      opacity: 0.6;
      filter: brightness(1.2);
    }
    75% { 
      opacity: 0.4;
      filter: brightness(1.1);
    }
  }

  @keyframes light-shine {
    0%, 100% { 
      opacity: 0.3;
      filter: brightness(1) blur(0px);
    }
    50% { 
      opacity: 0.6;
      filter: brightness(1.3) blur(1px);
    }
  }

  @keyframes dark-pulse {
    0%, 100% { 
      opacity: 0.3;
      box-shadow: inset 0 0 10px rgba(102, 68, 170, 0.3);
    }
    50% { 
      opacity: 0.5;
      box-shadow: inset 0 0 15px rgba(75, 0, 130, 0.5);
    }
  }

  @keyframes generic-pulse {
    0%, 100% { 
      opacity: 0.2;
    }
    50% { 
      opacity: 0.3;
    }
  }

  /* Overlay UI inside portrait */
  .overlay-ui {
    position: absolute;
    bottom: 4px;
    right: 4px;
    display: flex;
    align-items: flex-end;
    gap: 6px;
    pointer-events: none;
  }

  .passive-indicators {
    --pip-size: clamp(4px, calc(var(--portrait-size) * 0.09), 12px);
    --pip-gap: clamp(2px, calc(var(--portrait-size) * 0.03), 4px);
    display: flex;
    gap: 2px;
    pointer-events: none;
  }
  .passive {
    background: var(--glass-bg);
    box-shadow: var(--glass-shadow);
    border: var(--glass-border);
    backdrop-filter: var(--glass-filter);
    padding: 0 4px;
    min-width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    line-height: 1;
  }
  .passive.pips-mode {
    background: transparent;
    box-shadow: none;
    border: none;
    padding: 0;
    min-width: 0;
    height: auto;
  }
  .passive.spinner-mode {
    background: transparent;
    box-shadow: none;
    border: none;
    padding: 0;
    min-width: 0;
    height: auto;
  }
  .passive.number-mode {
    background: rgba(0,0,0,0.35);
    box-shadow: inset 0 0 0 2px color-mix(in oklab, var(--element-color, #6cf) 60%, black);
    border: none;
    backdrop-filter: none;
    border-radius: 6px;
    padding: 0 6px;
    min-width: unset;
    height: unset;
  }
  .pips { display: flex; gap: var(--pip-gap); line-height: 0; }
  :global(.pip-icon) {
    width: var(--pip-size);
    height: var(--pip-size);
    display: block;
    color: rgba(0, 0, 0, 0.55);
    stroke: none;
    fill: currentColor;
    transition: color 0.2s;
  }
  :global(.pip-icon.filled) { color: var(--element-color); }
  .passive-indicators.reduced :global(.pip-icon) { transition: none; }
  .passive-indicators.reduced :global(.pip-icon.filled) { transform: none; }
  .count {
    font-size: clamp(0.9rem, calc(var(--portrait-size) * 0.11), 1.2rem);
    line-height: 1;
    font-weight: 900;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.9);
  }

  .pip-row {
    display: flex;
    gap: 4px;
    align-items: center;
    margin-right: 2px;
  }
  .pip {
    width: calc(var(--portrait-size) * 0.05);
    height: calc(var(--portrait-size) * 0.05);
    border-radius: 2px;
    background: rgba(255,255,255,0.25);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2);
  }
  .pip.filled { background: color-mix(in oklab, var(--element-color, #6cf) 50%, black); }

  /* Numeric actions indicator (used by Luna, Carly, etc.) */
  .pip-number {
    position: relative;
    min-width: calc(var(--portrait-size) * 0.18);
    height: calc(var(--portrait-size) * 0.18);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: calc(var(--portrait-size) * 0.10);
    color: #fff;
    background: rgba(0,0,0,0.35);
    box-shadow: inset 0 0 0 2px color-mix(in oklab, var(--element-color, #6cf) 60%, black);
    text-shadow: 0 1px 2px rgba(0,0,0,0.9);
    pointer-events: none;
  }

  /* Ult gauge: bottom-up fill with subtle wave */
  .ult-gauge {
    position: relative;
    width: calc(var(--portrait-size) * 0.32);
    height: calc(var(--portrait-size) * 0.32);
    border-radius: 50%;
    background: rgba(0,0,0,0.35);
    overflow: hidden;
    border: 2px solid color-mix(in oklab, var(--element-color, #6cf) 60%, black);
  }
  /* Soft faded-edge backdrop around the ult gauge */
  .ult-gauge::before {
    content: '';
    position: absolute;
    inset: -10px;
    border-radius: 50%;
    background: radial-gradient(
      circle at center,
      rgba(0, 0, 0, 0.55) 0%,
      rgba(0, 0, 0, 0.45) 40%,
      rgba(0, 0, 0, 0.25) 70%,
      rgba(0, 0, 0, 0.00) 100%
    );
    filter: blur(4px);
    pointer-events: none;
    z-index: -1;
  }
  .ult-fill {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: calc(var(--p, 0) * 100%);
    /* Solid single-color fill based on the element color */
    background: color-mix(in oklab, var(--element-color, #6cf) 68%, black);
  }
  /* Breathing pulse while charging; speeds up as --p increases */
  .ult-pulse {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    pointer-events: none;
    background: radial-gradient(circle,
      color-mix(in oklab, var(--element-color, #6cf) 30%, white) 0%,
      transparent 70%);
    opacity: 0.15;
    mix-blend-mode: screen;
    animation-name: ult-breathe;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
  }
  @keyframes ult-breathe {
    0%, 100% { transform: scale(0.95); opacity: 0.12; }
    50% { transform: scale(1.05); opacity: 0.25; }
  }
  /* Soft feather at the fill boundary when not full */
  .ult-gauge:not(.ult-ready)::after {
    content: '';
    position: absolute;
    left: 0; right: 0;
    height: 14px;
    bottom: calc((var(--p, 0) * 100%) - 7px);
    background: linear-gradient(
      to top,
      color-mix(in oklab, var(--element-color, #6cf) 70%, black) 0%,
      color-mix(in oklab, var(--element-color, #6cf) 35%, black) 70%,
      rgba(0,0,0,0) 100%
    );
    filter: blur(3px);
    opacity: 0.75;
    pointer-events: none;
  }
  .ult-ready .ult-fill { filter: drop-shadow(0 0 8px var(--element-color)); }
  .ult-glow {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: radial-gradient(circle, color-mix(in oklab, var(--element-color, #6cf) 50%, white) 0%, transparent 70%);
    opacity: 0.22;
    animation: ult-pulse 1.4s ease-in-out infinite;
  }
  @keyframes ult-pulse {
    0%, 100% { transform: scale(1); opacity: 0.25; }
    50% { transform: scale(1.08); opacity: 0.45; }
  }

  /* Dead state */
  .dead .fighter-portrait {
    opacity: 0.4;
    filter: grayscale(100%);
    /* Keep outline element-colored even when dead for consistency */
    border-color: var(--element-color, rgba(255, 255, 255, 0.3));
  }

  .dead .element-effect {
    display: none;
  }

  /* Size variants */
  .small .element-indicator {
    width: 12px;
    height: 12px;
    font-size: 6px;
  }

  /* Hover effects */
  .fighter-portrait:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .dead .fighter-portrait:hover {
    transform: none;
  }

  /* Position-specific styling removed to keep outlines element-colored */

  /* Responsive adjustments */
  @media (max-width: 600px) {
    /* No element indicator; overlay UI scales naturally */
  }
</style>
