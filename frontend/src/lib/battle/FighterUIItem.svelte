<script>
  import { getCharacterImage, getElementColor, getElementIcon } from '../systems/assetLoader.js';

  export let fighter = {};
  export let position = 'bottom'; // 'top' for foes, 'bottom' for party
  export let reducedMotion = false;
  export let size = 'normal'; // 'normal' or 'small'

  $: elColor = getElementColor(fighter.element);
  $: portraitSize = size === 'small' ? '40px' : '60px';
  
  // Element-specific glow effects for different damage types
  $: elementGlow = getElementGlow(fighter.element);
  
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
      class:element-glow={!reducedMotion && !isDead}
      style="background-image: url({getCharacterImage(fighter)})"
    >
      {#if !reducedMotion && !isDead}
        <div class="element-effect {elementGlow.effect}"></div>
      {/if}
    </div>
    
    <!-- Element indicator -->
    <div class="element-indicator" style="background-color: {elColor}">
      <span class="element-icon">{getElementIcon(fighter.element)}</span>
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
    border: 2px solid rgba(255, 255, 255, 0.3);
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

  .element-indicator {
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.5);
    font-size: 8px;
  }

  .element-icon {
    color: #fff;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }

  /* Dead state */
  .dead .fighter-portrait {
    opacity: 0.4;
    filter: grayscale(100%);
    border-color: rgba(255, 0, 0, 0.5);
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

  /* Position-specific styling */
  .top .fighter-portrait {
    border-color: rgba(255, 100, 100, 0.5);
  }

  .bottom .fighter-portrait {
    border-color: rgba(100, 255, 100, 0.5);
  }

  /* Responsive adjustments */
  @media (max-width: 600px) {
    .element-indicator {
      width: 14px;
      height: 14px;
      font-size: 7px;
    }

    .small .element-indicator {
      width: 10px;
      height: 10px;
      font-size: 5px;
    }
  }
</style>